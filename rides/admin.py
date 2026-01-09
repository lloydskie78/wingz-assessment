from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Ride, RideEvent


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    
    list_display = ['id_user', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin interface for Ride model."""
    
    list_display = ['id_ride', 'status', 'id_rider', 'id_driver', 'pickup_time']
    list_filter = ['status', 'pickup_time']
    search_fields = ['id_rider__email', 'id_driver__email']
    raw_id_fields = ['id_rider', 'id_driver']


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    """Admin interface for RideEvent model."""
    
    list_display = ['id_ride_event', 'id_ride', 'description', 'created_at']
    list_filter = ['created_at', 'description']
    search_fields = ['description', 'id_ride__id_ride']
    raw_id_fields = ['id_ride']

