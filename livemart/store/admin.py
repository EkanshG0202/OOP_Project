from django.contrib import admin
from .models import Category, Product, Inventory, Feedback

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_region_specific')
    list_filter = ('category', 'is_region_specific')
    search_fields = ('name', 'description')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'retailer', 'wholesaler', 'price', 'stock')
    list_filter = ('retailer', 'wholesaler')
    search_fields = ('product__name',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'created_at')
    list_filter = ('product', 'customer', 'rating')

