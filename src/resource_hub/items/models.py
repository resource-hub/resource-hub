import uuid

from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from resource_hub.core.models import (Actor, BaseModel, BaseStateMachine,
                                      Claim, Contract, ContractProcedure,
                                      Gallery, Location, Price)
from resource_hub.core.utils import get_valid_slug


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

    def _send_running_notification(self, request):
        item_instructions = ''
        item_attachments = []
        for item in self.items.all():
            item_instructions += item.instructions
            if item.attachment:
                item_attachments.append(item.attachment.path)
        message = '{} \n {} \n {} \n'.format(
            self.note,
            self.contract_procedure.notes,
            item_instructions).replace("\n", "<br />\n")
        self._send_state_notification(
            sender=self.creditor,
            recipient=self.debitor,
            header=_('{creditor} accepted {contract}'.format(
                creditor=self.creditor,
                contract=self.verbose_name,
            )),
            message=message,
            request=request,
            attachments=item_attachments,
        )

    def purge(self):
        super(ItemContract, self).purge()
        self.bookings.all().soft_delete()

    def claim_factory(self, **kwargs):
        if self.is_self_dealing:
            return
        net_total = 0
        for booking in self.bookings.all():
            start = booking.dtstart if booking.item.unit == Item.UNIT.HOURS else booking.dtstart.date()
            end = booking.dtend if booking.item.unit == Item.UNIT.HOURS else booking.dtend.date()
            timedelta = end - start
            delta = (timedelta.total_seconds()) / \
                3600 if booking.item.unit == Item.UNIT.HOURS else timedelta.days
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
                period_start=start,
                period_end=end,
            )

            net_total += net

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


class Item(BaseStateMachine):
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

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )
    slug = models.SlugField(
        db_index=True,
        max_length=50,
        verbose_name=_('Slug'),
    )
    custom_id = models.CharField(
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('Custom ID'),
        help_text=_('ID field for bardcodes etc.'),
    )
    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Description'),
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
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name=_('Location'),
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
    base_price = models.ForeignKey(
        Price,
        null=True,
        on_delete=models.PROTECT,
        related_name='item_base_price',
        verbose_name=_('Base price'),
    )
    contract_procedure = models.ForeignKey(
        ItemContractProcedure,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name=_('Contract procedure'),
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
    attachment = models.FileField(
        null=True,
        blank=True,
        verbose_name=_('Attachment'),
        help_text=_('This file will be attached to the confirmation mail'),
    )
    thumbnail_original = models.ImageField(
        null=False,
        upload_to='images/',
        verbose_name=_('Thumbnail'),
        default='images/default.png',
    )
    thumbnail = ImageSpecField(
        source='thumbnail_original',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70},
    )
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Gallery'),
    )
    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Purchase date'),
    )
    purchase_price = models.ForeignKey(
        Price,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='item_purchase_price',
        verbose_name=_('Purchase price'),
    )
    replacement_price = models.ForeignKey(
        Price,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='item_replacement_price',
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

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(Item(), self.name)
        super(Item, self).save(*args, **kwargs)


class ItemPrice(Price):
    item = models.ForeignKey(
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
