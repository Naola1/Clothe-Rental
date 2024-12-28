from rest_framework import serializers
from shop.models import Clothes, Category, Rental, Cart, CartItem
from django.utils import timezone
from datetime import datetime

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']
        read_only_fields = ['slug']  

class ClothesSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Clothes
        fields = ['id', 'name', 'description', 'category', 'category_id', 
                 'size', 'color', 'price', 'image', 'availability', 
                 'rating', 'stock', 'condition', 'views_count']
        read_only_fields = ['views_count']  

class RentalCreateSerializer(serializers.ModelSerializer):
    clothe_id = serializers.PrimaryKeyRelatedField(
        queryset=Clothes.objects.filter(availability=True, stock__gt=0),
        source='clothe'
    )
    rental_date = serializers.DateField(required=True)
    
    class Meta:
        model = Rental
        fields = ['clothe_id', 'rental_date', 'duration']

    def validate_rental_date(self, value):
        # Convert date to datetime for comparison
        today = timezone.now().date()
        if value < today:
            raise serializers.ValidationError("Rental date cannot be in the past")
        return value

    def validate(self, data):
        # Check if user already has an active rental for this item
        user = self.context['request'].user
        existing_rental = Rental.objects.filter(
            user=user,
            clothe=data['clothe'],
            status='active'
        ).exists()
        
        if existing_rental:
            raise serializers.ValidationError(
                "You already have an active rental for this item"
            )
        
        return data

class RentalDetailSerializer(serializers.ModelSerializer):
    clothe = ClothesSerializer(read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'clothe', 'status', 'rental_date', 'duration',
                 'return_date', 'total_price', 'late_fee', 'is_extended',
                 'extended_return_date', 'notes']
        read_only_fields = fields
class CartItemSerializer(serializers.ModelSerializer):
    clothes = ClothesSerializer(read_only=True)
    clothes_id = serializers.PrimaryKeyRelatedField(
        queryset=Clothes.objects.filter(availability=True, stock__gt=0),
        source='clothes',
        write_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
        source='get_total_price'
    )

    class Meta:
        model = CartItem
        fields = ['id', 'clothes', 'clothes_id', 'quantity', 'total_price']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, data):
        """Validate if requested quantity is available in stock"""
        clothes = data['clothes']
        quantity = data['quantity']
        
        if quantity > clothes.stock:
            raise serializers.ValidationError(
                f"Only {clothes.stock} items available in stock"
            )
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_total_price'
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at']