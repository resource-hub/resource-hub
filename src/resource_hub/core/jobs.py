from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

import django_rq
from django_rq import job
from resource_hub.core.models import Contract


def init_schedule():
    scheduler = django_rq.get_scheduler('default')
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),  # Time for first execution, in UTC timezone
        func=expire_contracts,                     # Function to be queued
        args=[],             # Arguments passed into function when executed
        interval=60,                   # Time before the function is called again, in seconds
        result_ttl=-1,
    )


@job('default')
def send_mail(subject, message, recipient):
    email = EmailMultiAlternatives(
        subject,
        message,
        to=recipient,
    )
    email.attach_alternative(message, 'text/html')

    email.send(fail_silently=False)


def expire_contracts():
    pending_contracts = Contract.objects.filter(
        state=Contract.STATE_PENDING)
    for contract in pending_contracts:
        if contract.is_expired:
            contract.set_expired()
