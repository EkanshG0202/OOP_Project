from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# --- OOP Class Design (Users) ---

class User(AbstractUser):
    """
    Custom User Model.
    We inherit from AbstractUser to get all of Django's auth features,
    and add our custom 'role' field.
    """
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        RETAILER = "RETAILER", "Retailer"
        WHOLESALER = "WHOLESALER", "Wholesaler"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    
    # --- FIX FOR CLASH ---
    # We must redefine the 'groups' and 'user_permissions' fields
    # to add a unique 'related_name' and solve the clash.
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        # This 'related_name' is now unique!
        related_name="custom_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        # This 'related_name' is also unique!
        related_name="custom_user_permissions",
        related_query_name="user",
    )
    
    def __str__(self):
        return self.username

# --- Profile Models ---

class CustomerProfile(models.Model):
    """Profile for a Customer, linked to the main User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='customerprofile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Customer: {self.user.username}"

class RetailerProfile(models.Model):
    """Profile for a Retailer, linked to the main User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='retailerprofile')
    shop_name = models.CharField(max_length=100)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"Retailer: {self.shop_name} ({self.user.username})"

class WholesalerProfile(models.Model):
    """Profile for a Wholesaler, linked to the main User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='wholesalerprofile')
    business_name = models.CharField(max_length=100)
    warehouse_location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Wholesaler: {self.business_name} ({self.user.username})"

