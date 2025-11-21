from django.db import models
from users.models import CustomerProfile, RetailerProfile
from store.models import Inventory

# --- OOP Class Design (Orders & Carts) ---

# =========================================
# === SHARED CHOICES (NEW)
# =========================================

class FulfillmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"

# =========================================
# === CUSTOMER CART & ORDER MODELS
# =========================================

class Cart(models.Model):
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.customer.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [['cart', 'inventory']]

    def __str__(self):
        return f"{self.quantity} x {self.inventory.product.name} in {self.cart}"


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        SHIPPED = "SHIPPED", "Shipped" # This could mean 'all items shipped'
        DELIVERED = "DELIVERED", "Delivered" # This could mean 'all items delivered'
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_offline_payment = models.BooleanField(default=False)
    shipping_address = models.TextField()

    # --- ADDED for Calendar Integration ---
    scheduled_delivery_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="For offline orders: The scheduled date/time for pickup or delivery."
    )
    # --------------------------------------

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.username} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT) 
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    
    # This is the fulfillment status for this specific item
    status = models.CharField(
        max_length=20, 
        choices=FulfillmentStatus.choices, 
        default=FulfillmentStatus.PENDING
    )

    class Meta:
        unique_together = [['order', 'inventory']]
        
    def __str__(self):
        return f"{self.quantity} x {self.inventory.product.name} in Order {self.order.id}"


# =========================================
# === WHOLESALE CART & ORDER MODELS
# =========================================

class WholesaleCart(models.Model):
    retailer = models.OneToOneField(RetailerProfile, on_delete=models.CASCADE, related_name='wholesale_cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wholesale Cart for {self.retailer.shop_name}"

class WholesaleCartItem(models.Model):
    cart = models.ForeignKey(WholesaleCart, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [['cart', 'inventory']]
        
    def __str__(self):
        return f"{self.quantity} x {self.inventory.product.name} in {self.cart}"

class WholesaleOrder(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        PROCESSING = "PROCESSING", "Processing" # e.g., Wholesalers are preparing items
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    retailer = models.ForeignKey(RetailerProfile, on_delete=models.CASCADE, related_name='wholesale_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField() 

    def __str__(self):
        return f"Wholesale Order {self.id} by {self.retailer.shop_name}"

class WholesaleOrderItem(models.Model):
    order = models.ForeignKey(WholesaleOrder, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    # Fulfillment status for this specific item
    status = models.CharField(
        max_length=20, 
        choices=FulfillmentStatus.choices, 
        default=FulfillmentStatus.PENDING
    )

    class Meta:
        unique_together = [['order', 'inventory']]

    def __str__(self):
        return f"{self.quantity} x {self.inventory.product.name} in Wholesale Order {self.order.id}"