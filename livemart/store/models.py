from django.db import models
from users.models import User, RetailerProfile, WholesalerProfile # Import User models

# --- PHASE 1: OOP Class Design (Store) ---

class Category(models.Model):
    """
    A simple model for product categories (e.g., "Dairy", "Vegetables").
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories" # Fixes admin panel's "Categorys"

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    This is the master list of all products in the system.
    e.g., "Amul Milk 1L", "Onions", "Parle-G Biscuit"
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    # A product belongs to one Category. This is a "Many-to-One" relationship.
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    # We can highlight local items
    is_region_specific = models.BooleanField(default=False)
    # Placeholder for a product image
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    """
    This is the key model that connects Products to Sellers (Retailers/Wholesalers).
    It stores the price and stock level for a specific product
    sold by a specific seller.
    This is a "Many-to-Many" relationship (via this "through" model).
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # We link to both profile types, but only one should be filled.
    # This shows who is selling this item.
    retailer = models.ForeignKey(RetailerProfile, on_delete=models.CASCADE, null=True, blank=True)
    wholesaler = models.ForeignKey(WholesalerProfile, on_delete=models.CASCADE, null=True, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    # For "proxy availability" - Retailer can list items they get from a wholesaler
    available_via_wholesaler = models.ForeignKey(WholesalerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="proxy_items")
    
    # Ensures a single inventory item per product per seller
    class Meta:
        unique_together = [['product', 'retailer'], ['product', 'wholesaler']]
        verbose_name_plural = "Inventories"

    def __str__(self):
        seller = self.retailer.shop_name if self.retailer else self.wholesaler.business_name
        return f"{self.product.name} at {seller} (Stock: {self.stock})"

class Feedback(models.Model):
    """
    Model for collecting product-specific feedback from customers.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="feedback")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback")
    rating = models.PositiveSmallIntegerField(default=5) # e.g., 1-5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A customer can only leave one review per product
        unique_together = [['product', 'customer']]

    def __str__(self):
        return f"Feedback for {self.product.name} by {self.customer.username}"
