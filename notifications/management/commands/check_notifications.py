from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notifications.models import RentalNotification
from notifications.services import EmailService

class Command(BaseCommand):
    help = 'Check and send scheduled notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        
        pending_notifications = RentalNotification.objects.filter(
            status='pending',
            scheduled_date__lte=now
        )

        for notification in pending_notifications:
            if notification.notification_type == 'return_reminder':
                EmailService.send_return_reminder(notification)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {pending_notifications.count()} notifications'
            )
        )

