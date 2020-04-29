
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .actors import Actor
from .base import BaseModel


class Notification(BaseModel):
    class LEVEL:
        '''
        the level of a message is the basis for user notification 
        preferences
        '''
        LOW = 0  # info
        MEDIUM = 1  # action required, mail
        HIGH = 2  # warning
        CRITICAL = 3  # mandatory information

    LEVELS = [
        (LEVEL.LOW, _('low')),
        (LEVEL.MEDIUM, _('medium')),
        (LEVEL.HIGH, _('high')),
        (LEVEL.CRITICAL, _('critical')),
    ]

    class TYPE:
        '''
        the type is based on the content of the message
        and determines the display of the notification
        '''
        INFO = 'i'
        ACTION = 'a'
        CONTRACT = 'c'
        MONETARY = 'm'

    TYPES = [
        (TYPE.INFO, _('info')),
        (TYPE.ACTION, _('action')),
        (TYPE.CONTRACT, _('contract')),
        (TYPE.MONETARY, _('monetary')),
    ]

    # mappings for semantic ui
    TYPE_ICON_MAP = {
        TYPE.INFO: 'info circle',
        TYPE.ACTION: 'bolt',
        TYPE.CONTRACT: 'handshake',
        TYPE.MONETARY: 'file alternate outline',
        'default': 'info circle',
    }

    class STATUS:
        '''
        The status indicates whether the message has been picked
        up and delivered via a secondary messaging service (e.g. mail)

        The type of service depends on the users preferences
        and settings
        '''
        PENDING = 'p'
        SENT = 's'

    STATI = [
        (STATUS.PENDING, _('pending')),
        (STATUS.SENT, _('send')),
    ]

    # fields
    status = models.CharField(
        max_length=1,
        choices=STATI,
        default=STATUS.PENDING,
    )
    typ = models.CharField(
        max_length=30,
        choices=TYPES,
    )
    sender = models.ForeignKey(
        'Actor',
        null=True,
        on_delete=models.SET_NULL,
        related_name='notification_sender',
    )
    recipient = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
        related_name='notification_recipient',
    )
    header = models.CharField(
        max_length=255,
    )
    message = models.TextField(
        null=True,
    )
    link = models.URLField()
    level = models.IntegerField(
        choices=LEVELS,
    )
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')
    is_read = models.BooleanField(
        default=False,
    )
    @property
    def type_(self):
        return self.typ

    # methods
    @classmethod
    def get_type_icon(cls, type_):
        return cls.TYPE_ICON_MAP.get(type_, cls.TYPE_ICON_MAP['default'])

    def send_mail(self, connection=None):
        from ..jobs import send_mail
        attachments_qs = NotificationAttachment.objects.filter(
            notification=self
        )
        attachments = []
        for attachment in attachments_qs:
            attachments.append(attachment.path)

        if self.level > Notification.LEVEL.LOW:
            recipient = Actor.objects.get_subclass(pk=self.recipient.pk)
            message = render_to_string('core/mail_notification.html', context={
                'recipient': recipient,
                'link': self.link,
                'message': self.message,
            })
            send_mail(
                subject=self.header,
                message=self.message,
                recipient=recipient.notification_recipients,
                attachments=attachments,
                connection=connection,
            )
        self.status = self.STATUS.SENT
        self.save()

    @classmethod
    def build(cls, type_, sender, recipient, header, message, link, level, target, attachments=None):
        notification = cls.objects.create(
            typ=type_,
            sender=sender,
            recipient=recipient,
            header=header,
            message=message,
            link=link,
            level=level,
            target=target,
        )

        if attachments:
            for attachment in attachments:
                notification.attachments.create(
                    path=attachment,
                )
        return notification

    @classmethod
    def send_open_mails(cls):
        connection = mail.get_connection()
        connection.open()
        for notification in cls.objects.filter(status=cls.STATUS.PENDING):
            notification.send_mail(connection)
        connection.close()


class NotificationAttachment(BaseModel):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.PROTECT,
        related_name='attachments',
    )
    path = models.CharField(
        max_length=255,
    )
