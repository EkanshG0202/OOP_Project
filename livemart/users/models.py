from django.db import models
from django.contrib.auth.models import AbstractUser

# --- PHASE 1: OOP Class Design (Users) ---
# This is the core of your user system.

class User(AbstractUser):
    """
    This is our custom User model.
    We INHERIT from Django's AbstractUser to get all the
    built-in fields like username, password, email, etc.

    We add a 'role' to manage our 3 different user types.
    """
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        RETAILER = "RETAILER", "Retailer"
        WHOLESALER = "WHOLESALER", "Wholesaler"

    # We set the default role to CUSTOMER.
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER)

    def __str__(self):
        return f"{self.username} ({self.role})"

# The following "Profile" models demonstrate a "One-to-One" relationship.
# Each User will have exactly one corresponding profile.
# This is a clean way to store role-specific data.

class CustomerProfile(models.Model):
    """
    Stores data specific to Customers.
    """
    # models.OneToOneField links this profile to one User.
    # on_delete=models.CASCADE means if the User is deleted, delete this profile.
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # We can store the Google Maps latitude/longitude for location features
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.user.username

class RetailerProfile(models.Model):
    """
    Stores data specific to Retailers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # We can add fields for tracking purchase history with wholesalers
    # (This will be linked via the Order model later)

    def __str__(self):
        return self.shop_name

class WholesalerProfile(models.Model):
    """
    Stores data specific to Wholesalers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    business_name = models.CharField(max_length=255)
    warehouse_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.business_name

