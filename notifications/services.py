from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email, subject, message):
        try:
            logger.info(f"Attempting to send email to {to_email}")
            result = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False,
            )
            logger.info(f"Email sent successfully: {result}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return str(e)

    @staticmethod
    def send_return_reminder(notification):
        try:
            logger.info(f"Preparing return reminder for notification {notification.id}")
            
            # Calculate days until return
            days_until_return = (notification.rental.return_date - timezone.now().date()).days
            
            # Prepare email content
            subject = f"Return Reminder for {notification.rental.clothe.name}"
            message = (
                f"Dear {notification.rental.user.username},\n\n"
                f"This is a reminder about your rental of {notification.rental.clothe.name}.\n"
                f"Return date: {notification.rental.return_date}\n"
                f"Days remaining: {days_until_return}\n\n"
                f"Please ensure to return the item on time to avoid any late fees.\n\n"
                f"Thank you for using our service!"
            )
            
            # Send email
            result = EmailService.send_email(
                notification.rental.user.email,
                subject,
                message
            )
            
            if isinstance(result, str):  # If result is error message
                logger.error(f"Failed to send notification {notification.id}: {result}")
                notification.status = 'failed'
                notification.error_message = result
                notification.save()
                return False
            
            # Update notification status on success
            logger.info(f"Successfully sent notification {notification.id}")
            notification.status = 'sent'
            notification.sent_date = timezone.now()
            notification.save()
            return True
            
        except Exception as e:
            logger.error(f"Exception in send_return_reminder: {str(e)}")
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
            raise
