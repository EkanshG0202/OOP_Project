from rest_framework import serializers
from .models import Category, Product, Inventory, Feedback
from users.models import User # We'll need this for feedback

# --- API Serializers (Store) ---

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    # We show the category name instead of just its ID
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'is_region_specific', 'image']

class InventorySerializer(serializers.ModelSerializer):
    # --- This is a Nested Serializer ---
    # It shows the full Product details, not just the product ID.
    product = ProductSerializer(read_only=True)
    
    # This adds a new field to the API, pulling data from a related model
    retailer_name = serializers.CharField(source='retailer.shop_name', read_only=True)
    wholesaler_name = serializers.CharField(source='wholesaler.business_name', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 
            'product', 
            'retailer', 
            'retailer_name', 
            'wholesaler',
            'wholesaler_name',
            'price', 
            'stock',
            'available_via_wholesaler'
        ]

class FeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'product', 'customer', 'customer_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['customer'] # Customer is set automatically

