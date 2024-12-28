from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify

# Category Model with unique slug
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# Clothes Model
class Clothes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='clothes')
    size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    #price = models.IntegerField(default = 0)
    image = models.ImageField(upload_to="clothes/")
    availability = models.BooleanField(default=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Rating from 1 to 5
    stock = models.PositiveIntegerField()
    condition = models.CharField(max_length=50, default="new")
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Rental Model
class Rental(models.Model):
    DURATION_CHOICES = [
        (2, "2 days"),
        (4, "4 days"),
        (8, "8 days"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
    ]
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name="rental_records")
    clothe = models.ForeignKey(Clothes, on_delete=models.CASCADE, related_name="rentals")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    rental_date = models.DateField(default=timezone.now)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    return_date = models.DateField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_extended = models.BooleanField(default=False)
    extended_return_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_price(self):
        return self.clothe.price * self.duration

    def calculate_return_date(self):
        duration_days = int(self.duration)
        return self.rental_date + timedelta(days=duration_days)


    def can_rent_again(self, user, cloth):
        """
        Check if a user can rent this cloth again
        """
        existing_rental = Rental.objects.filter(
            user=user, 
            clothe=cloth, 
            status='active'
        ).exists()
        return not existing_rental
     
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        if not self.return_date:
            self.return_date = self.calculate_return_date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rental of {self.clothe.name} for {self.duration} days"

# Cart Model
class Cart(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        """
        Calculate total price of all items in cart
        """
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'Anonymous'}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'clothes')

    def get_total_price(self):
        return self.clothes.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.clothes.name}"