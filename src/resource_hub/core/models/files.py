import string
from tempfile import TemporaryFile

from django.core.files import File as DjFile
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from django_ical import feedgenerator

from .base import BaseModel


def build_path(instance, filename: str) -> str:
    secret = get_random_string(
        length=16,
        allowed_chars=string.ascii_letters + string.digits,
    )
    return 'files/{owner_pk}/{file_dir}/{file_id}--{secret}.{ext}'.format(
        owner_pk=instance.owner.pk,
        file_dir=instance.directory,
        file_id=instance.identifier,
        secret=secret,
        ext=filename.split('.')[-1],
    )


class File(BaseModel):
    '''
    A class for linking various files to actors for making sure they get deleted when the user leaves
    '''

    # fields
    file = models.FileField(
        upload_to=build_path,
        verbose_name=_('file'),
        max_length=255,
    )
    owner = models.ForeignKey(
        'Actor',
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('actor'),
    )

    @property
    def directory(self) -> str:
        return 'default'

    @property
    def identifier(self) -> str:
        return self.pk


class ICSFile(File):
    meta = {}
    items = []

    @property
    def directory(self):
        return 'ics'

    @property
    def identifier(self):
        return 'calendar-{pk}'.format(
            pk=self.pk
        )

    def set_meta(self, **meta):
        self.meta = meta

    def add_item(self, **item):
        self.items.append(item)

    def create_file(self):
        feed = feedgenerator.ICal20Feed(
            **self.meta,
        )
        for item in self.items:
            feed.add_item(
                **item,
            )
        filename = 'feed.ics'
        with TemporaryFile(mode='wb+') as f:
            feed.write(f, 'utf-8')
            self.file.save(filename, DjFile(f))
