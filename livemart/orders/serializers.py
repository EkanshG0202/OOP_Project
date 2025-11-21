from rest_framework import serializers
from .models import (
    Cart, CartItem, Order, OrderItem,
    WholesaleCart, WholesaleCartItem, WholesaleOrder, WholesaleOrderItem,
    FulfillmentStatus # --- IMPORTED ---
)
from store.serializers import InventorySerializer
from users.models import User, RetailerProfile
from store.models import Inventory

# --- API Serializers (Orders) ---

# =========================================
# === CUSTOMER CART & ORDER SERIALIZERS
# =========================================

class CartItemSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    inventory_id = serializers.PrimaryKeyRelatedField(
        queryset=Inventory.objects.all(),
        source='inventory',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'inventory', 'inventory_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.username', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'customer_name', 'created_at', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    status = serializers.CharField(read_only=True) # --- ADDED (Customer can't change it) ---
    
    class Meta:
        model = OrderItem
        fields = ['id', 'inventory', 'quantity', 'price_at_purchase', 'status'] # --- ADDED 'status' ---


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
            'items',
            'scheduled_delivery_date'
        ]

# =========================================
# === RETAILER-FACING ORDER SERIALIZERS
# =========================================

class RetailerOrderItemSerializer(serializers.ModelSerializer):
    """
    Shows OrderItem details relevant to a retailer.
    --- THIS IS NOW WRITABLE FOR THE 'status' FIELD ---
    """
    inventory = InventorySerializer(read_only=True)
    customer_username = serializers.CharField(source='order.customer.user.username', read_only=True)
    shipping_address = serializers.CharField(source='order.shipping_address', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order_id',
            'order_status',
            'customer_username',
            'shipping_address',
            'inventory', 
            'quantity', 
            'price_at_purchase',
            'status' # --- ADDED 'status' ---
        ]
        # --- ADDED: Allow Retailer to PATCH the status, but nothing else ---
        read_only_fields = [
            'id',
            'order_id',
            'order_status',
            'customer_username',
            'shipping_address',
            'inventory', 
            'quantity', 
            'price_at_purchase',
        ]

class RetailerOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 
            'customer_name', 
            'created_at', 
            'status', 
            'shipping_address',
            'items'
        ]
    
    def get_items(self, obj):
        retailer_profile = self.context['request'].user.retailerprofile
        retailer_items = obj.items.filter(inventory__retailer=retailer_profile)
        # --- Use the OrderItemSerializer to show the new status ---
        serializer = OrderItemSerializer(retailer_items, many=True, read_only=True)
        return serializer.data


# =========================================
# === WHOLESALE CART & ORDER SERIALIZERS
# =========================================

class WholesaleCartItemSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    inventory_id = serializers.PrimaryKeyRelatedField(
        queryset=Inventory.objects.filter(wholesaler__isnull=False),
        source='inventory',
        write_only=True
    )

    class Meta:
        model = WholesaleCartItem
        fields = ['id', 'inventory', 'inventory_id', 'quantity']

class WholesaleCartSerializer(serializers.ModelSerializer):
    items = WholesaleCartItemSerializer(many=True, read_only=True)
    retailer_name = serializers.CharField(source='retailer.shop_name', read_only=True)

    class Meta:
        model = WholesaleCart
        fields = ['id', 'retailer', 'retailer_name', 'created_at', 'items']


class WholesaleOrderItemSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    status = serializers.CharField(read_only=True) # --- ADDED (Retailer can't change) ---
    
    class Meta:
        model = WholesaleOrderItem
        fields = ['id', 'inventory', 'quantity', 'price_at_purchase', 'status'] # --- ADDED 'status' ---

class WholesaleOrderSerializer(serializers.ModelSerializer):
    # --- UPDATED: Use the new Order Item serializer ---
    items = WholesaleOrderItemSerializer(many=True, read_only=True)
    retailer_name = serializers.CharField(source='retailer.shop_name', read_only=True)

    class Meta:
        model = WholesaleOrder
        fields = [
            'id',
            'retailer',
            'retailer_name',
            'created_at',
            'status',
            'total_price',
            'delivery_address',
            'items'
        ]

# =========================================
# === WHOLESALER-FACING SERIALIZERS (NEW)
# =========================================

class WholesalerFulfillmentItemSerializer(serializers.ModelSerializer):
    """
    Shows WholesaleOrderItem details to a Wholesaler
    and allows them to update the status.
    """
    inventory = InventorySerializer(read_only=True)
    retailer_name = serializers.CharField(source='order.retailer.shop_name', read_only=True)
    delivery_address = serializers.CharField(source='order.delivery_address', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)

    class Meta:
        model = WholesaleOrderItem
        fields = [
            'id',
            'order_id',
            'order_status',
            'retailer_name',
            'delivery_address',
            'inventory', 
            'quantity', 
            'price_at_purchase',
            'status' # This is the only writable field
        ]
        read_only_fields = [
            'id',
            'order_id',
            'order_status',
            'retailer_name',
            'delivery_address',
            'inventory', 
            'quantity', 
            'price_at_purchase',
        ]