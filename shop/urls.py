from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home', views.home_view, name='home'),
    path('cloth/<int:cloth_id>/', views.cloth_detail_view, name='cloth_detail'),
    path('rented/', views.rented_items, name='rented_list'),
    path('rentals/', views.rented_items, name='rented_items'),
    path('rentals/<int:rental_id>/extend/', views.extend_rental, name='extend_rental'),
    path('add-to-cart/<int:cloth_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:cloth_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    
]

