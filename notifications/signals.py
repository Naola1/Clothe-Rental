from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from shop.models import Rental
from .models import RentalNotification
from .services import EmailService

@receiver(post_save, sender=Rental)
def create_rental_notifications(sender, instance, created, **kwargs):
    if created:
        # Create return reminder notification (1 day before return date)
        reminder_date = instance.return_date - timedelta(days=1)
        notification = RentalNotification.objects.create(
            rental=instance,
            notification_type='return_reminder',
            status='pending',
            scheduled_date=timezone.make_aware(timezone.datetime.combine(reminder_date, timezone.datetime.min.time()))
        )

#