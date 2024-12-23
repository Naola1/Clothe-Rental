from django.contrib import admin
from .models import Clothes, Rental, Category, Cart, CartItem

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    list_filter = ["name"]
    search_fields = ["name", "parent"]
    list_per_page = 20


@admin.register(Clothes)
class ClothesAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "availability", "rating", "stock", "condition", "views_count", "created_at", "updated_at"]
    list_filter = ["availability", "rating", "condition"]
    search_fields = ["name", "price", "availability", "rating", "stock", "condition", "views_count"]
    list_per_page = 20


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(children__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ["clothe", "status", "rental_date", "duration", "total_price", "return_date", "late_fee", "is_extended", "created_at"]
    list_filter = ["status", "duration", "is_extended"]
    search_fields = ["clothe", "status", "rental_date", "duration", "total_price", "return_date", "late_fee", "is_extended"]
    list_per_page = 20
 
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1  

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]  

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'clothes', 'quantity')  
    search_fields = ('clothes__name',)


