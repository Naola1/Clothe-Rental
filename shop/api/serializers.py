from rest_framework import serializers
from shop.models import Clothes, Category, Rental, Cart, CartItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']

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