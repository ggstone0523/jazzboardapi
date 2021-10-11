from config.settings import EMAIL_HOST_USER
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email(title, content, email):
    send_mail(
        subject=title,
        message=content,
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )
    return None