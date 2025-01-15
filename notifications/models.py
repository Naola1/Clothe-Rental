from django.db import models
from django.utils import timezone
from shop.models import Rental

class RentalNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('return_reminder', 'Return Reminder'),
        ('overdue_notice', 'Overdue Notice'),
        ('rental_confirmation', 'Rental Confirmation'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.notification_type} for {self.rental.user.email}"

