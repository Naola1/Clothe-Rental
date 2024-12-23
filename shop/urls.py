from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home_view, name='home'),
    path('', views.home_view, name='home'),
    path('cloth/<int:cloth_id>/', views.cloth_detail_view, name='cloth_detail'),
    path('rented/', views.rented_items, name='rented_list'),
    path('rentals/', views.rented_items, name='rented_items'),
    path('rentals/<int:rental_id>/extend/', views.extend_rental, name='extend_rental'),
]