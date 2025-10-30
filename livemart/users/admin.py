from django.contrib import admin
from .models import User, CustomerProfile, RetailerProfile, WholesalerProfile

# --- PHASE 3: Admin Dashboard Setup ---
# This code registers your models with the Django Admin site.
# This gives you an instant, secure backend to manage your users.

# We can customize the admin view
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role']
    search_fields = ['username', 'email']

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'address']
    search_fields = ['user__username', 'phone_number']

class RetailerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop_name', 'shop_address']
    search_fields = ['user__username', 'shop_name']

class WholesalerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'warehouse_address']
    search_fields = ['user__username', 'business_name']


# Register your models here
admin.site.register(User, UserAdmin)
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(RetailerProfile, RetailerProfileAdmin)
admin.site.register(WholesalerProfile, WholesalerProfileAdmin)
