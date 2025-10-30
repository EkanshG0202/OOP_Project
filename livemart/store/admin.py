from django.contrib import admin
from .models import Category, Product, Inventory, Feedback

# --- PHASE 3: Admin Dashboard Setup ---
# Registering the store models

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_region_specific']
    list_filter = ['category', 'is_region_specific']
    search_fields = ['name', 'description']

class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'retailer', 'wholesaler', 'price', 'stock']
    list_filter = ['retailer', 'wholesaler']
    search_fields = ['product__name', 'retailer__shop_name', 'wholesaler__business_name']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'customer__username']


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Feedback, FeedbackAdmin)
