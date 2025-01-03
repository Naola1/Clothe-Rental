from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from shop.models import Rental
from .models import RentalNotification
import datetime

@receiver(post_save, sender=Rental)
def create_rental_notifications(sender, instance, created, **kwargs):
    """Create notifications when a new rental is created"""
    if created:
       
        reminder_date = datetime.datetime.strptime(instance.return_date, '%Y-%m-%d')
        reminder_date = reminder_date - datetime.timedelta(days=1)
        reminder_date = reminder_date.replace(hour=0, minute=0, second=0)
        
        RentalNotification.objects.create(
            rental=instance,
            notification_type='return_reminder',
            scheduled_date=reminder_date
        )