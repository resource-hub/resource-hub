
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .actors import Actor
from .base import BaseModel, BaseStateMachine


class Notification(BaseStateMachine):
    class LEVEL:
        '''
        the level of a message is the basis for user
        notification preferences
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

    class STATE(BaseStateMachine.STATE):
        '''
        The status indicates whether the message has been picked
        up and delivered via a secondary messaging service (e.g. mail)

        The type of service depends on the users preferences
        and settings
        '''
        SENT = 's'

    STATE_GRAPH = {
        STATE.PENDING: {STATE.SENT}
    }

    # fields
    typ = models.CharField(
        max_length=30,
        choices=TYPES,
        verbose_name=_('Type'),
    )
    sender = models.ForeignKey(
        'Actor',
        null=True,
        on_delete=models.SET_NULL,
        related_name='notification_sender',
        verbose_name=_('Sender'),
    )
    recipient = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
        related_name='notification_recipient',
        verbose_name=_('Recipient'),
    )
    header = models.CharField(
        max_length=255,
        verbose_name=_('Header'),
    )
    message = models.TextField(
        null=True,
        verbose_name=_('Message'),
    )
    link = models.URLField(
        verbose_name=_('Link'),
    )
    level = models.IntegerField(
        choices=LEVELS,
        verbose_name=_('Level'),
    )
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Read?'),
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
                message=message,
                recipient=recipient.notification_recipients,
                attachments=attachments,
                connection=connection,
            )
        self.move_to(self.STATE.SENT)
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
        for notification in cls.objects.filter(state=cls.STATE.PENDING):
            notification.send_mail(connection)
        connection.close()


class NotificationAttachment(BaseModel):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.PROTECT,
        related_name='attachments',
        verbose_name=_('Notification'),
    )
    path = models.CharField(
        max_length=255,
        verbose_name=_('Path'),
    )
