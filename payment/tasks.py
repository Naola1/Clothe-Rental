from celery import shared_task
from django.core.mail import send_mail
from .models import Payment

@shared_task
def send_payment_success_email(payment_id):
    payment = Payment.objects.get(id=payment_id)
    subject = "Payment Successful"
    message = f"Your payment of ${payment.amount} was successful."
    recipient = [payment.user.email]
    send_mail(subject, message, 'your_email@example.com', recipient)
