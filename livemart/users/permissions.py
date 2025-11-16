from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User

class IsCustomer(BasePermission):
    """
    Allows access only to users with the 'CUSTOMER' role.
    """
    message = "You must be a customer to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.CUSTOMER
        )

class IsRetailer(BasePermission):
    """
    Allows access only to users with the 'RETAILER' role.
    """
    message = "You must be a retailer to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.RETAILER
        )

class IsWholesaler(BasePermission):
    """
    Allows access only to users with the 'WHOLESALER' role.
    """
    message = "You must be a wholesaler to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.WHOLESALER
        )

class IsSeller(BasePermission):
    """
    Allows access only to users with 'RETAILER' or 'WHOLESALER' roles.
    """
    message = "You must be a retailer or wholesaler to perform this action."
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.RETAILER, User.Role.WHOLESALER]
        )

class IsOwnerOfInventory(BasePermission):
    """
    Object-level permission to only allow owners of an inventory item to edit it.
    Assumes the object has 'retailer' or 'wholesaler' attributes.
    """
    message = "You do not have permission to edit this inventory item."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request (e.g., GET, HEAD, OPTIONS)
        # This is handled by the View's get_permissions() method.
        # This check is for write permissions.
        if obj.retailer:
            return obj.retailer.user == request.user
        if obj.wholesaler:
            return obj.wholesaler.user == request.user
        return False

class IsOwnerOfFeedbackOrReadOnly(BasePermission):
    """
    Object-level permission to only allow the customer who wrote feedback to edit it.
    Allows read-only for all other requests.
    """
    message = "You do not have permission to edit this feedback."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the customer who wrote it
        return obj.customer == request.user