# notifications/services.py
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import RentalNotification

class EmailService:
    @staticmethod
    def send_email(to_email, subject, content):
        try:
            send_mail(
                subject=subject,
                message=content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            return str(e)

    @classmethod
    def send_return_reminder(cls, notification):
        rental = notification.rental
        subject = "Reminder: Your Rental Return is Due Tomorrow"
        content = f"""
        Dear {rental.user.username},

        This is a friendly reminder that your rental of {rental.clothe.name} is due tomorrow.

        Rental Details:
        - Item: {rental.clothe.name}
        - Return Date: {rental.return_date}

        Please ensure to return the item on time to avoid any late fees.

        Best regards,
        FashionFlex Team
        """
        
        result = cls.send_email(rental.user.email, subject, content)
        if result is True:
            notification.status = 'sent'
            notification.sent_date = timezone.now()
            notification.save()
        else:
            notification.status = 'failed'
            notification.error_message = str(result)
            notification.save()

