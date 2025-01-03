from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from freezegun import freeze_time
from .models import RentalNotification
from .services import EmailService
from shop.models import Rental, Clothes, Category
from user.models import User

class NotificationTests(TestCase):
    @patch('notifications.signals.EmailService.send_return_reminder')
    def setUp(self, mock_send_reminder):
        mock_send_reminder.return_value = True
        
        self.user = User.objects.create_user(
            username='testuser',
            email='naolmitiku85@gmail.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category"
        )
        
        self.clothe = Clothes.objects.create(
            category=self.category,
            name="Test Dress",
            description="A test dress",
            size="M",
            color="Blue",
            price=100.00,
            stock=1,
            condition="new",
            availability=True
        )
        
        # Create rental with future return date
        self.rental = Rental.objects.create(
            user=self.user,
            clothe=self.clothe,
            status="active",
            rental_date=timezone.now().date(),
            duration=7,  
            return_date=timezone.now().date() + timedelta(days=7)
        )
        
        self.notification = RentalNotification.objects.get(rental=self.rental)
        mock_send_reminder.reset_mock()

    def test_notification_creation(self):
        """Test that notification is created correctly with rental"""
        self.assertEqual(self.notification.notification_type, 'return_reminder')
        self.assertEqual(self.notification.status, 'pending')
        self.assertEqual(
            self.notification.scheduled_date.date(),
            self.rental.return_date - timedelta(days=1)
        )

    @patch('notifications.services.EmailService.send_email')
    @freeze_time("2024-01-01 12:00:00")
    def test_early_reminder(self, mock_send_email):
        """Test sending reminder before the scheduled date"""
        mock_send_email.return_value = True
        
        # Set rental return date to 3 days from now
        self.rental.return_date = timezone.now().date() + timedelta(days=3)
        self.rental.save()
        
        # Update notification scheduled date
        self.notification.scheduled_date = timezone.now() + timedelta(days=2)
        self.notification.save()
        
        # Send reminder
        result = EmailService.send_return_reminder(self.notification)
        
        self.assertTrue(result)
        self.assertEqual(self.notification.status, 'sent')
        mock_send_email.assert_called_once()

    @patch('notifications.services.EmailService.send_email')
    def test_email_failure_handling(self, mock_send_email):
        """Test handling of email sending failures"""
        mock_send_email.return_value = "SMTP error"
        
        result = EmailService.send_return_reminder(self.notification)
        
        self.assertFalse(result)
        self.assertEqual(self.notification.status, 'failed')
        self.assertEqual(self.notification.error_message, "SMTP error")

