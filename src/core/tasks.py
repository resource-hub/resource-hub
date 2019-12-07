import asyncio


async def send_mail(subject, message, recipient):
    email = EmailMultiAlternatives(
        subject,
        message,
        to=[recipient],
    )
    email.attach_alternative(message, 'text/html')

    email.send(fail_silently=False)


class Tasks():
    def send_mail(subject, message, recipient):
        task = asyncio.create_task(send_mail(subject, message, recipient))
        asyncio.run_loop(task)
