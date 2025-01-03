from django.urls import path
from . import views


urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('extend/<int:rental_id>/', views.extend_rental, name='extend_rental'), 
    path('cart-payment/', views.cart_payment, name='cart_payment'),
    path('cart-success/', views.cart_payment_success, name='cart_success'),
    path('payments/success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('payments/extension-success/', views.extension_success, name='extension_success'),
]