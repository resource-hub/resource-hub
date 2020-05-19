import uuid

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from resource_hub.core.models import (Actor, BaseModel, BaseStateMachine,
                                      Contract, ContractProcedure, Gallery,
                                      Location, Price)


class ItemContractProcedure(ContractProcedure):
    self_pickup_group = models.ManyToManyField(
        Actor,
        blank=True,
        help_text=_(
            'The group granted self pickup if item\'s self pickup is limited')
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
    )


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
    )
    custom_id = models.CharField(
        max_length=100,
        help_text=_('ID field for bardcodes etc.'),
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=64,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    manufacturer = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )
    model = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )
    serial_no = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='items',
    )
    location_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    quantity = models.IntegerField(
        default=1,
    )
    unit = models.CharField(
        max_length=3,
        choices=UNITS,
        default=UNIT.DAYS,
    )
    base_price = models.ForeignKey(
        Price,
        on_delete=models.PROTECT,
        related_name='item_base_price',
    )
    contract_procedure = models.ForeignKey(
        ItemContractProcedure,
        on_delete=models.PROTECT,
        related_name='items',
    )
    maximum_duration = models.IntegerField(
        default=0,
        help_text=_(
            'Maximimum duration the item can be lent. Value of 0 means unlimited.'),
    )
    self_pickup = models.CharField(
        max_length=2,
        default=SELF_PICKUP.NOT_ALLOWED,
        choices=SELF_PICKUPS,
    )
    damages = models.TextField(
        null=True,
        blank=True,
    )
    category = models.CharField(
        choices=CATEGORIES,
        default=CATEGORY.OTHER,
        max_length=3,
    )
    instructions = models.TextField(
        null=True,
        blank=True,
        help_text=_(
            'These instructions will be included in the confirmation mail text'),
    )
    attachment = models.FileField(
        null=True,
        blank=True,
        help_text=_('This file will be attached to the confirmation mail'),
    )
    thumbnail_original = models.ImageField(
        null=False,
        upload_to='images/',
        verbose_name=_('thumbnail'),
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
        null=True
    )
    purchase_date = models.DateField(
        null=True,
        blank=True,
    )
    purchase_price = models.ForeignKey(
        Price,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='item_purchase_price',
    )
    replacement_price = models.ForeignKey(
        Price,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='item_replacement_price',
    )
    donation = models.BooleanField(
        default=False,
        null=True,
        blank=True,
    )
    original_owner = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Which entity bought or donated the item?'),
    )
    owner = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
        related_name='items',
    )


class ItemPrice(Price):
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='prices',
    )


class ItemBooking(BaseModel):
    contract = models.ForeignKey(
        ItemContract,
        on_delete=models.PROTECT,
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
    )
    dtstart = models.DateTimeField()
    dtend = models.DateTimeField()
