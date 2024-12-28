from rest_framework import viewsets, status, filters, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from shop.filters import ClotheFilter
from shop.models import Clothes, Category, Rental, Cart, CartItem
from .serializers import (
    ClothesSerializer, CategorySerializer, 
    RentalCreateSerializer, CartItemSerializer, 
    CartSerializer, RentalDetailSerializer, 
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

class CategoryViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Category.objects.all()
        parent = self.request.query_params.get('parent', None)
        if parent is not None:
            queryset = queryset.filter(parent__slug=parent)
        return queryset

class ClothesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Clothes.objects.filter(stock__gt=0)
    serializer_class = ClothesSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClotheFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'rating', 'created_at']

class RentalViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RentalCreateSerializer
        return RentalDetailSerializer

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Calculate total price and save with user
        clothe = serializer.validated_data['clothe']
        duration = serializer.validated_data['duration']
        total_price = clothe.price * duration
        
        # Decrease stock
        clothe.stock -= 1
        clothe.save()
        
        serializer.save(
            user=self.request.user,
            status='active',
            total_price=total_price
        )

    @action(detail=True, methods=['post'])
    def extend_rental(self, request, pk=None):
        rental = self.get_object()
        if rental.status != 'active':
            return Response(
                {'error': 'Only active rentals can be extended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        days = request.data.get('days', 0)
        try:
            days = int(days)
            if days <= 0:
                raise ValueError
            
            # Calculate additional price
            additional_price = rental.clothe.price * days
            
            # Update rental
            rental.extended_return_date = rental.return_date + timedelta(days=days)
            rental.total_price += additional_price
            rental.is_extended = True
            rental.save()
            
            return Response({
                'status': 'rental extended',
                'new_return_date': rental.extended_return_date,
                'additional_charge': additional_price
            })
        except ValueError:
            return Response(
                {'error': 'Invalid number of days'},
                status=status.HTTP_400_BAD_REQUEST
            )

class CartViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    ViewSet for managing shopping cart operations.
    Supports:
    - Viewing cart
    - Adding items
    - Removing items
    - Updating quantities
    - Clearing cart
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get or create cart for current user"""
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(id=cart.id)

    def get_cart(self):
        """Helper method to get current user's cart"""
        return Cart.objects.get_or_create(user=self.request.user)[0]

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add item to cart or update quantity if item exists
        """
        cart = self.get_cart()
        clothes_id = request.data.get('clothes_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            clothes = Clothes.objects.get(id=clothes_id, availability=True)
            
            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                clothes=clothes,
                defaults={'quantity': quantity}
            )

            if not created:
                # Update quantity if item exists
                cart_item.quantity += quantity
                if cart_item.quantity > clothes.stock:
                    return Response({
                        'error': f'Only {clothes.stock} items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
                cart_item.save()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)

        except Clothes.DoesNotExist:
            return Response({
                'error': 'Item not found or not available'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                'error': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """
        Remove item from cart
        """
        cart = self.get_cart()
        item_id = request.data.get('item_id')

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                id=item_id
            )
            cart_item.delete()
            
            # Return updated cart data
            serializer = CartSerializer(cart)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response({
                'error': 'Item not found in cart'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """
        Update item quantity in cart
        """
        cart = self.get_cart()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError

            cart_item = CartItem.objects.get(
                cart=cart,
                id=item_id
            )

            # Check stock availability
            if quantity > cart_item.clothes.stock:
                return Response({
                    'error': f'Only {cart_item.clothes.stock} items available in stock'
                }, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = quantity
            cart_item.save()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response({
                'error': 'Item not found in cart'
            }, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        """
        Remove all items from cart
        """
        cart = self.get_cart()
        cart.items.all().delete()
        return Response({
            'message': 'Cart cleared successfully'
        })

    @action(detail=False, methods=['get'])
    def cart_summary(self, request):
        """
        Get cart summary with total items and price
        """
        cart = self.get_cart()
        total_items = sum(item.quantity for item in cart.items.all())
        total_price = cart.get_total_price()

        return Response({
            'total_items': total_items,
            'total_price': total_price,
            'items_count': cart.items.count()
        })