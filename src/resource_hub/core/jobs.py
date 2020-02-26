from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

import django_rq
from django_rq import job
from resource_hub.core.models import Contract


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
