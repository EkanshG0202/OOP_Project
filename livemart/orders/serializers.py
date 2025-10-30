from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from store.serializers import InventorySerializer

# --- API Serializers (Orders) ---

class CartItemSerializer(serializers.ModelSerializer):
    # Nested serializer to show item details
    inventory = InventorySerializer(read_only=True)
    # We also need a write-only field to *create* a cart item
    inventory_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'inventory', 'inventory_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    # Nest all the items belonging to this cart
    items = CartItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.username', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'customer_name', 'created_at', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'inventory', 'quantity', 'price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 
            'customer', 
            'customer_name', 
            'created_at', 
            'status', 
            'total_price',
            'is_offline_payment',
            'shipping_address',
            'items'
        ]
        read_only_fields = ['customer', 'total_price', 'status']

