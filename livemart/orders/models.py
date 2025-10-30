from django.db import models
from users.models import CustomerProfile
from store.models import Inventory

# --- OOP Class Design (Orders & Carts) ---

class Cart(models.Model):
    """
    A Customer's shopping cart.
    We use a One-to-One link to the Customer's profile.
    """
    customer = models.OneToOneField(CustomerProfile, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.customer.user.username}"

class CartItem(models.Model):
    """
    An item *in* a cart.
    This links a Cart to a specific Inventory item.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # We link to Inventory, not Product, because the user is buying
    # a specific product from a specific retailer at a specific price.
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Ensures a customer can't add the same inventory item twice
        unique_together = [['cart', 'inventory']]

    def __str__(self):
        return f"{self.quantity} x {self.inventory.product.name} in {self.cart}"


class Order(models.Model):
    """
    An Order placed by a customer.
    This is created *after* checkout.
    """
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # We can store the shipping address, payment type (online/offline) etc.
    is_offline_payment = models.BooleanField(default=False)
    shipping_address = models.TextField()

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.username} ({self.status})"


class OrderItem(models.Model):
    """
    A single item *in* a placed order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT) # Protect from deletion
    quantity = models.PositiveIntegerField()
    
    # --- CRITICAL ---
    # We store the price at the time of purchase.
    # This prevents the order total from changing if the
    # retailer updates their inventory price later.
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.inventory.product.name} in Order {self.order.id}"

