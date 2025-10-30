from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('customer', 'created_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('inventory', 'quantity', 'price_at_purchase')

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'customer', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'is_offline_payment')
    readonly_fields = ('customer', 'total_price')

admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
