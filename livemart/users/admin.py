from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, RetailerProfile, WholesalerProfile

# We're just modifying the base User admin to show our new 'role' field
class CustomUserAdmin(BaseUserAdmin):
    model = User
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Role', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    list_filter = ('role', 'is_staff', 'is_superuser')

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')

# --- THIS IS THE FIX ---
@admin.register(RetailerProfile)
class RetailerProfileAdmin(admin.ModelAdmin):
    # We replace 'shop_address' with the actual fields:
    # 'location_lat' and 'location_lon'
    list_display = ('user', 'shop_name', 'location_lat', 'location_lon')

# --- THIS IS THE FIX ---
@admin.register(WholesalerProfile)
class WholesalerProfileAdmin(admin.ModelAdmin):
    # We replace 'warehouse_address' with the actual field:
    # 'warehouse_location'
    list_display = ('user', 'business_name', 'warehouse_location')

# Unregister the base User admin and register our custom one
# We check if the default User is registered before unregistering
if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

