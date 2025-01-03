from django.db import models
# from django.contrib.auth.models import User
from shop.models import Clothes

class Payment(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    cloth = models.ForeignKey(Clothes, on_delete=models.CASCADE,null=True, blank=True)  
    stripe_payment_intent = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    is_extended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    payment_type = models.CharField(
        max_length=50, 
        choices=[
            ('initial_rental', 'Initial Rental'),
            ('rental_extension', 'Rental Extension')
        ],
        default='initial_rental'
    )

    def __str__(self):
        return f"Payment for {self.cloth.name} by {self.user.username}"