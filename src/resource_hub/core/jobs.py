from datetime import datetime, timedelta

from django.core import mail
from django.db.models import Max
from django.utils import timezone

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
    ### contracts ###
    # expire contracts
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=expire_contracts,
        args=[],
        interval=60,
    )
    # settle claims
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=settle_claims,
        args=[],
        interval=600,
    )
    # send notification mails
    scheduler.schedule(
        scheduled_time=datetime.utcnow(),
        func=send_notification_mails,
        args=[],
        interval=10,
    )


def expire_contracts():
    pending_contracts = Contract.objects.filter(
        state=Contract.STATE.PENDING).select_subclasses()
    for contract in pending_contracts:
        if contract.is_expired:
            contract.set_expired()


@job('default')
def send_mail(subject, message, recipient, attachments=None, connection=None):
    '''
    :param connection can only be used if job is executed synchonously
    as connection objects cannot be pickled by RQ
    '''
    if connection:
        email = mail.EmailMultiAlternatives(
            subject,
            message,
            to=recipient,
            connection=connection,
        )

    else:
        email = mail.EmailMultiAlternatives(
            subject,
            message,
            to=recipient,
        )
    email.attach_alternative(message, 'text/html')
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment)

    email.send(fail_silently=False)


@job('high')
def send_notification_mails():
    Notification.send_open_mails()


@job('low')
def settle_claims():
    for contract in Contract.objects.filter(state=Contract.STATE.RUNNING):
        if contract.contract_procedure:
            last_settlement = contract.settlement_logs.aggregate(
                Max('timestamp'))
            if timezone.now() - timedelta(days=contract.contract_procedure.settlement_interval) < last_settlement['timestamp__max']:
                contract.settle_claims()
