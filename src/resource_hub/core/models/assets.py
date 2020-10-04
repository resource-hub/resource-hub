
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from .base import BaseModel, Gallery, Location
from .finance import Price


class AssetMixin(models.Model):
    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
    )
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
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Description'),
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        verbose_name=_('Location'),
        help_text=_('All public and current role\'s locations'),
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
    base_price = models.ForeignKey(
        Price,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('Base price'),
    )

    class Meta:
        abstract = True


class BaseAsset(AssetMixin, BaseModel):
    class Meta:
        abstract = True
