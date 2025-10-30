from rest_framework import viewsets, permissions, mixins
from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from users.models import CustomerProfile # Need this for cart creation

# --- API Views (Orders) ---

class CartViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for the user's shopping cart.
    We only allow retrieving the cart.
    Adding/deleting items will be custom actions.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # A user can only see their own cart
        try:
            profile = self.request.user.customerprofile
            return Cart.objects.filter(customer=profile)
        except CustomerProfile.DoesNotExist:
            return Cart.objects.none()

    def get_object(self):
        # Get or create a cart for the user
        profile, created = CustomerProfile.objects.get_or_create(user=self.request.user)
        cart, created = Cart.objects.get_or_create(customer=profile)
        return cart

    def list(self, request, *args, **kwargs):
        # The 'list' action should just return the single cart
        # for the current user, not a list of all carts.
        return self.retrieve(request, *args, **kwargs)


class OrderViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for placing and viewing orders.
    'list' = get all my orders
    'retrieve' = get one specific order
    'create' = place a new order (checkout)
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own orders
        try:
            return Order.objects.filter(customer=self.request.user.customerprofile).order_by('-created_at')
        except CustomerProfile.DoesNotExist:
            return Order.objects.none()
    
    # We will add the 'create' logic (checkout) in the next phase!

