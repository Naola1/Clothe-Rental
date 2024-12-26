from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from shop.filters import ClotheFilter
from shop.models import Clothes, Category, Rental, Cart, CartItem
from .serializers import (
    ClothesSerializer, CategorySerializer, 
    
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Category.objects.all()
        parent = self.request.query_params.get('parent', None)
        if parent is not None:
            queryset = queryset.filter(parent__slug=parent)
        return queryset

class ClothesViewSet(viewsets.ModelViewSet):
    queryset = Clothes.objects.filter(stock__gt=0)
    serializer_class = ClothesSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClotheFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'rating', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category_slug', None)
        if category_slug:
            category = Category.objects.get(slug=category_slug)
            all_categories = [category] + get_all_child_categories(category)
            queryset = queryset.filter(category__in=all_categories)
        return queryset