from datetime import datetime

from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

import django_rq
from django_rq import job
from resource_hub.core.models import Contract, Notification


def clear_schedule():
    scheduler = django_rq.get_scheduler('default')
    old_jobs = scheduler.get_jobs()
    for old_job in old_jobs:
        scheduler.cancel(old_job)


def init_schedule():
    scheduler = django_rq.get_scheduler('default')
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=expire_contracts,
        args=[],
        interval=60,
    )


def expire_contracts():
    pending_contracts = Contract.objects.filter(
        state=Contract.STATE.PENDING).select_subclasses()
    for contract in pending_contracts:
        if contract.is_expired:
            contract.set_expired()


@job('default')
def send_mail(subject, message, recipient):
    email = EmailMultiAlternatives(
        subject,
        message,
        to=recipient,
    )
    email.attach_alternative(message, 'text/html')

    email.send(fail_silently=False)
    print(email.recipients())


@job('high')
def notify(sender, action, target, link, recipient, level, message):
    notification = Notification.objects.create(
        sender=sender,
        action=action,
        target=target,
        link=link,
        recipient=recipient,
        level=level,
        message=message,
    )
    if level > Notification.LEVEL.LOW:
        footer = _('See the link %(link)s for further information.') % {
            'link': link}
        message = message + footer
        send_mail.delay(
            '{} {} {}'.format(
                sender, notification.get_action_display(), target
            ),
            message,
            ['tu.cl@pm.me', 'test@ture.dev', ],
        )
