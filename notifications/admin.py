from django.contrib import admin
from .models import RentalNotification

@admin.register(RentalNotification)
class RentalNotificationAdmin(admin.ModelAdmin):
    list_display = ('rental', 'scheduled_date') 