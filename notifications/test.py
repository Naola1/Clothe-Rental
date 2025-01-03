# notifications/tests.py
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from unittest.mock import patch
from datetime import timedelta
from .models import RentalNotification
from .services import EmailService
from shop.models import Rental, Clothes, Category
from user.models import User

class NotificationTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create category
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category"
        )

        # Create clothes
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

        # Create rental
        self.rental = Rental.objects.create(
            user=self.user,
            clothe=self.clothe,
            status="active",
            rental_date=timezone.now().date(),
            duration=1,
            return_date=timezone.now().date() + timedelta(days=1)
        )

    def test_notification_creation_on_rental(self):
        """Test that notification is created automatically when rental is created"""
        notifications = RentalNotification.objects.filter(rental=self.rental)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications[0].notification_type, 'return_reminder')

    def test_email_sending(self):
        """Test actual email sending"""
        notification = RentalNotification.objects.get(rental=self.rental)
        EmailService.send_return_reminder(notification)
        
        # Test that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)
        
        # Test that notification was marked as sent
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'sent')

    def test_command_sends_due_notifications(self):
        """Test that management command sends due notifications"""
        notification = RentalNotification.objects.get(rental=self.rental)
        notification.scheduled_date = timezone.now() - timedelta(minutes=1)
        notification.save()

        # Run command
        from notifications.management.commands.check_notifications import Command
        command = Command()
        command.handle()

        # Check notification was sent
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'sent')
        self.assertEqual(len(mail.outbox), 1)

    def test_command_skips_future_notifications(self):
        """Test that command doesn't send future notifications"""
        notification = RentalNotification.objects.get(rental=self.rental)
        notification.scheduled_date = timezone.now() + timedelta(days=1)
        notification.save()

        # Run command
        from notifications.management.commands.check_notifications import Command
        command = Command()
        command.handle()

        # Check notification wasn't sent
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'pending')
        self.assertEqual(len(mail.outbox), 0)

    def test_email_failure_handling(self):
        """Test handling of email sending failures"""
        notification = RentalNotification.objects.get(rental=self.rental)
        
        # Simulate email failure
        with patch('django.core.mail.send_mail', side_effect=Exception('Email failed')):
            EmailService.send_return_reminder(notification)
        
        # Check notification was marked as failed
        notification.refresh_from_db()
        self.assertEqual(notification.status, 'failed')
        self.assertIn('Email failed', notification.error_message)

    def tearDown(self):
        # Clean up
        self.user.delete()
        self.category.delete()
        self.clothe.delete()
        mail.outbox = []