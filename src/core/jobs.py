from django.core.mail import EmailMultiAlternatives
from django_rq import job


@job('high')
def send_mail(subject, message, recipient):
    email = EmailMultiAlternatives(
        subject,
        message,
        to=recipient,
    )
    email.attach_alternative(message, 'text/html')

    email.send(fail_silently=False)
