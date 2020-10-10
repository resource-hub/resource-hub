import datetime

from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from resource_hub.core.models import (Actor, AssetMixin, BaseModel,
                                      BaseStateMachine, Claim, Contract,
                                      ContractProcedure, File, Gallery,
                                      ICSFile, Location, Notification, Price)
from resource_hub.core.utils import get_valid_slug, language


class ItemContractProcedure(ContractProcedure):
    self_pickup_group = models.ManyToManyField(
        Actor,
        blank=True,
        help_text=_(
            'The group granted self pickup if item\'s self pickup is limited'),
        verbose_name=_('Self pickup group'),
    )

    @property
    def type_name(self):
        return _('Item contract procedure')

    @property
    def form_link(self):
        return reverse('control:items_contract_procedures_create')

    @property
    def edit_link(self):
        return reverse('control:items_contract_procedures_edit', kwargs={'pk': self.pk})


class ItemContract(Contract):
    items = models.ManyToManyField(
        'Item',
        related_name='contracts',
        through='ItemBooking',
        verbose_name=_('Item'),
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Note'),
        help_text=_(
            'This message will be sent to the owner. This allows to negiotate pickup times etc.'),
    )

    @property
    def verbose_name(self):
        return _('Item booking')

    @property
    def overview(self):
        return render_to_string(
            'items/_contract_overview.html',
            context={
                'contract': self,
            }
        )

    def _get_waiting_notification_msg(self):
        return self.note

    def _get_running_notification_msg(self):
        item_instructions = ''
        for item in self.items.all():
            item_instructions += item.instructions
        return '{} \n {} \n'.format(
            self.contract_procedure.notes,
            item_instructions).replace("\n", "<br />\n")

    def _get_running_notification_attachments(self):
        item_attachments = super(
            ItemContract, self)._get_running_notification_attachments()
        item_attachments.append(self._create_ics_file())
        return item_attachments

    def _create_ics_file(self):
        link = reverse('control:finance_contracts_manage_details',
                       kwargs={'pk': self.pk})
        reciever = self.debitor
        with language(reciever.language):
            file = ICSFile.objects.create(
                owner=reciever,
            )
            file.set_meta(
                title=_('Item rental %(contract)s') % {'contract': self.uuid},
                link=link,
                language=reciever.language,
                description=_('An item rental on resource hub'),
            )
            for booking in self.bookings.all():
                file.add_item(
                    title=_('Rental of %(item)s') % {
                        'item': booking.item.name,
                    },
                    link=link,
                    description=_('An item rental on resource hub'),
                    start_datetime=booking.dtstart,
                    end_datetime=booking.dtend,
                )
            file.create_file()
            return file

    def purge(self):
        super(ItemContract, self).purge()
        self.bookings.all().soft_delete()

    def claim_factory(self, **kwargs):
        if self.is_self_dealing:
            return
        net_total = 0
        currency = ''
        start = datetime.datetime(
            year=datetime.MAXYEAR, month=12, day=31, tzinfo=datetime.timezone.utc)
        end = datetime.datetime(year=datetime.MINYEAR,
                                month=1, day=1, tzinfo=datetime.timezone.utc)
        for booking in self.bookings.all():
            if booking.dtstart < start:
                start = booking.dtstart
            if booking.dtend > end:
                end = booking.dtend
            timedelta = (booking.dtend - booking.dtstart).total_seconds()
            delta = timedelta / \
                3600 if booking.item.unit_hours else timedelta / 86400
            net = delta * float(booking.item.base_price.value)
            discounted_net = self.price_profile.apply(
                net) if self.price_profile else net
            gross = self.contract_procedure.apply_tax(discounted_net)

            Claim.objects.create(
                contract=self,
                item=booking.item.name,
                quantity=delta,
                unit=booking.item.unit,
                price=booking.item.base_price.value,
                currency=booking.item.base_price.currency,
                net=net,
                discount=self.price_profile.discount if self.price_profile else 0,
                discounted_net=discounted_net,
                tax_rate=self.contract_procedure.tax_rate,
                gross=gross,
                period_start=booking.dtstart,
                period_end=booking.dtend,
            )

            net_total += net
        self.create_fee_claims(
            net_total, booking.item.base_price.currency, start, end)

    def set_waiting(self, request):
        super(ItemContract, self).set_waiting(request)
        # make sure contract hasn't already been auto accepted
        if self.state == self.STATE.WAITING:
            query = Q(self_pickup=Item.SELF_PICKUP.ALLOWED)
            sub_query = Q(self_pickup=Item.SELF_PICKUP.LIMITED)
            subsub_query = Q(
                contract_procedure__self_pickup_group=self.debitor)
            subsub_query.add(
                Q(contract_procedure__self_pickup_group__organization__members=self.debitor), Q.OR)
            sub_query.add(subsub_query, Q.AND)
            query.add(sub_query, Q.OR)
            if self.items.filter(query).exists():
                self.set_running(request)

    def set_terminated(self, initiator):
        super(ItemContract, self).set_terminated(initiator)
        self.bookings.filter(dtend__gte=timezone.now()).soft_delete()


class Item(AssetMixin, BaseStateMachine):
    class STATE:
        AVAILABLE = 'a'
        LENT = 'l'
        DEFECT = 'd'
        HIDDEN = 'h'

    STATES = [
        (STATE.AVAILABLE, _('available')),
        (STATE.LENT, _('lent')),
        (STATE.DEFECT, _('defect')),
        (STATE.HIDDEN, _('hidden')),
    ]

    STATE_GRAPH = {
        STATE.AVAILABLE: {STATE.DEFECT, STATE.HIDDEN, STATE.LENT, },
        STATE.LENT: {STATE.AVAILABLE, },
        STATE.DEFECT: {STATE.AVAILABLE, },
        STATE.HIDDEN: {STATE.AVAILABLE, },
    }

    class CATEGORY:
        VEHILCES = 'v'
        TOOLS = 't'
        ELECTRONICS = 'e'
        RECREATION = 'r'
        PHOTOGRAPHY = 'p'
        VIDEO = 'vi'
        OTHER = 'o'

    CATEGORIES = [
        (CATEGORY.VEHILCES, _('vehicles')),
        (CATEGORY.TOOLS, _('tools')),
        (CATEGORY.ELECTRONICS, _('electronics')),
        (CATEGORY.PHOTOGRAPHY, _('photography')),
        (CATEGORY.VIDEO, _('video')),
        (CATEGORY.OTHER, _('other')),
    ]

    class UNIT:
        HOURS = 'h'
        DAYS = 'd'

    UNITS = [
        (UNIT.HOURS, _('hours')),
        (UNIT.DAYS, _('days')),
    ]

    class SELF_PICKUP:
        NOT_ALLOWED = 'n'
        LIMITED = 'l'
        ALLOWED = 'a'

    SELF_PICKUPS = [
        (SELF_PICKUP.NOT_ALLOWED, _('not allowed')),
        (SELF_PICKUP.LIMITED, _('limited')),
        (SELF_PICKUP.ALLOWED, _('allowed')),
    ]

    contract_procedure = models.ForeignKey(
        ItemContractProcedure,
        on_delete=models.PROTECT,
        verbose_name=_('Contract procedure'),
    )
    custom_id = models.CharField(
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('Custom ID'),
        help_text=_('ID field for bardcodes etc.'),
    )
    manufacturer = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('Manufacturer'),
    )
    model = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('Model'),
    )
    serial_no = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Serial number'),
    )
    location_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Location code'),
    )
    quantity = models.IntegerField(
        default=1,
        verbose_name=_('Quantity'),
    )
    unit = models.CharField(
        max_length=3,
        choices=UNITS,
        default=UNIT.DAYS,
        verbose_name=_('Unit'),
    )
    maximum_duration = models.IntegerField(
        default=0,
        verbose_name=_('Maximum duration'),
        help_text=_(
            'Maximimum duration the item can be lent. Value of 0 means unlimited.'),
    )
    self_pickup = models.CharField(
        max_length=2,
        default=SELF_PICKUP.NOT_ALLOWED,
        choices=SELF_PICKUPS,
        verbose_name=_('Self pickup'),
    )
    damages = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Damages'),
    )
    category = models.CharField(
        choices=CATEGORIES,
        default=CATEGORY.OTHER,
        max_length=3,
        verbose_name=_('Category'),
    )
    instructions = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Instructions'),
        help_text=_(
            'These instructions will be included in the confirmation mail text'),
    )
    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Purchase date'),
    )
    purchase_price = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Purchase price'),
    )
    replacement_price = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Replacement price'),
    )
    donation = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_('Donation'),
    )
    original_owner = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Original owner'),
        help_text=_('Which entity bought or donated the item?'),
    )
    owner = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name=_('Owner'),
    )

    class Meta:
        unique_together = ('owner', 'slug')

    @property
    def unit_hours(self):
        return self.unit == Item.UNIT.HOURS

    @property
    def unit_days(self):
        return self.unit == Item.UNIT.DAYS

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(
                Item(), self.name, Q(owner=self.owner))
        super(Item, self).save(*args, **kwargs)


class ItemPrice(Price):
    item_ptr = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='prices',
        verbose_name=_('Item'),
    )


class ItemBooking(BaseModel):
    contract = models.ForeignKey(
        ItemContract,
        on_delete=models.PROTECT,
        verbose_name=_('Contract'),
        related_name='bookings'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        verbose_name=_('Item'),
    )
    dtstart = models.DateTimeField(
        verbose_name=_('Start'),

    )
    dtend = models.DateTimeField(
        verbose_name=_('End'),

    )
    quantity = models.IntegerField(
        default=1,
        verbose_name=_('Quantity'),
    )
