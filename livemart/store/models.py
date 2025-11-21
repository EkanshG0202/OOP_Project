from django.db import models
from users.models import User, RetailerProfile, WholesalerProfile

# --- OOP Class Design (Store) ---

class Category(models.Model):
    """Product categories (e.g., Dairy, Vegetables, Electronics)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    """A generic product (e.g., "Amul Milk 1L")."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    # Use ImageField for product images. Requires 'Pillow' to be installed.
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_region_specific = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    """
    This is the core "for-sale" item.
    It links a Product to a Seller (Retailer or Wholesaler)
    and gives it a price and stock level.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items')
    
    # A product can be sold by a Retailer OR a Wholesaler
    retailer = models.ForeignKey(RetailerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory')
    wholesaler = models.ForeignKey(WholesalerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory')
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    # For Module 2: Retailer's proxy availability
    available_via_wholesaler = models.BooleanField(default=False)

    # --- MERGED FIELD ---
    availability_date = models.DateField(null=True, blank=True, help_text="Date when the item will be available if out of stock.")
    # --------------------

    class Meta:
        verbose_name_plural = "Inventories"

    def __str__(self):
        # Handle cases where retailer or wholesaler might be None safely
        seller_name = "Unknown Seller"
        if self.retailer:
            seller_name = self.retailer.shop_name
        elif self.wholesaler:
            seller_name = self.wholesaler.business_name
            
        return f"{self.product.name} at {seller_name} (Stock: {self.stock})"

class Feedback(models.Model):
    """Model for product-specific feedback from customers."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveIntegerField() # e.g., 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.product.name} by {self.customer.username}"