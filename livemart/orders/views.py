from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from django.db import transaction

# --- ADDED IMPORTS FOR EMAIL ---
from django.core.mail import send_mail
from django.conf import settings
# -------------------------------

from .models import (
    Cart, CartItem, Order, OrderItem,
    WholesaleCart, WholesaleCartItem, WholesaleOrder, WholesaleOrderItem
)
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer,
    RetailerOrderSerializer, RetailerOrderItemSerializer,
    WholesaleCartSerializer, WholesaleCartItemSerializer, WholesaleOrderSerializer,
    WholesalerFulfillmentItemSerializer 
)
from users.models import CustomerProfile, RetailerProfile, WholesalerProfile
from store.models import Inventory

# --- Import our custom permissions ---
from users.permissions import IsCustomer, IsRetailer, IsWholesaler

# =========================================
# === CUSTOMER-FACING VIEWS
# =========================================

class CartItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for adding, updating, and removing items
    from the user's cart.
    ACCESS: Customers only.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        """ Users can only see and manage their own cart items. """
        try:
            return CartItem.objects.filter(cart__customer=self.request.user.customerprofile)
        except CustomerProfile.DoesNotExist:
            return CartItem.objects.none()

    def create(self, request, *args, **kwargs):
        """ Custom logic for adding an item to the cart. """
        try:
            profile = request.user.customerprofile
            cart, _ = Cart.objects.get_or_create(customer=profile)
        except CustomerProfile.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)

        inventory_id = request.data.get('inventory_id')
        quantity = int(request.data.get('quantity', 1))

        if not inventory_id:
            return Response({"error": "inventory_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Customers can only buy from retailers
            inventory = Inventory.objects.get(
                id=inventory_id, 
                stock__gt=0, 
                retailer__isnull=False
            )
        except Inventory.DoesNotExist:
            return Response({"error": "Retailer inventory item not found or is out of stock."}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            inventory=inventory,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if cart_item.quantity > inventory.stock:
            return Response(
                {"error": f"Not enough stock. Only {inventory.stock} available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(cart_item)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK, headers=headers)


class CartViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for viewing the user's cart.
    Provides a custom 'checkout' action.
    ACCESS: Customers only.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        try:
            return Cart.objects.filter(customer=self.request.user.customerprofile)
        except CustomerProfile.DoesNotExist:
            return Cart.objects.none()

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(customer=self.request.user.customerprofile)
        return cart

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """ Converts the user's cart into an order. """
        try:
            cart = self.get_object()
        except CustomerProfile.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if not cart.items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = request.data.get('shipping_address', cart.customer.address)
        is_offline_payment = bool(request.data.get('is_offline_payment', False))

        if not shipping_address:
            return Response(
                {"error": "Shipping address is required. Please provide one or update your profile."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_items_to_create = []
        total_price = 0

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=cart.customer,
                    status=Order.OrderStatus.PENDING,
                    total_price=0,
                    shipping_address=shipping_address,
                    is_offline_payment=is_offline_payment
                )

                cart_items = cart.items.all()
                inventory_ids = [item.inventory_id for item in cart_items]
                inventories = Inventory.objects.select_for_update().filter(id__in=inventory_ids)
                inventory_map = {inv.id: inv for inv in inventories}

                for item in cart_items:
                    inventory = inventory_map.get(item.inventory_id)

                    if not inventory or item.quantity > inventory.stock:
                        raise ValidationError(f"Sorry, '{item.inventory.product.name}' is out of stock. Only {inventory.stock} left.")

                    inventory.stock -= item.quantity
                    inventory.save()

                    price_at_purchase = inventory.price
                    total_price += (price_at_purchase * item.quantity)
                    
                    order_items_to_create.append(
                        OrderItem(
                            order=order,
                            inventory=inventory,
                            quantity=item.quantity,
                            price_at_purchase=price_at_purchase
                            # Status defaults to PENDING
                        )
                    )

                order.total_price = total_price
                order.save()
                OrderItem.objects.bulk_create(order_items_to_create)
                cart.items.all().delete()

            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred during checkout: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing a customer's order history.
    ACCESS: Customers only.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        try:
            return Order.objects.filter(customer=self.request.user.customerprofile).order_by('-created_at')
        except CustomerProfile.DoesNotExist:
            return Order.objects.none()

# =========================================
# === RETAILER-FACING VIEWS
# =========================================

class RetailerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for a Retailer to view orders
    that contain their products.
    ACCESS: Retailers only.
    """
    serializer_class = RetailerOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_queryset(self):
        try:
            return Order.objects.filter(
                items__inventory__retailer=self.request.user.retailerprofile
            ).distinct().order_by('-created_at')
        except RetailerProfile.DoesNotExist:
            return Order.objects.none()
    
    def get_serializer_context(self):
        return {'request': self.request}


class RetailerOrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for a Retailer to view and UPDATE the status
    of *individual order items* that belong to them.
    ACCESS: Retailers only.
    """
    serializer_class = RetailerOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]
    
    # Allow GET, PATCH, PUT. Disallow POST, DELETE.
    http_method_names = ['get', 'patch', 'put', 'head', 'options']

    def get_queryset(self):
        """
        Retailers can only see and update order items 
        from their inventory.
        """
        try:
            return OrderItem.objects.filter(
                inventory__retailer=self.request.user.retailerprofile
            ).select_related(
                'order', 
                'order__customer__user', 
                'inventory__product'
            ).order_by('-order__created_at')
        except RetailerProfile.DoesNotExist:
            return OrderItem.objects.none()

    # --- ADDED: Email Notification Logic ---
    def perform_update(self, serializer):
        instance = serializer.save()
        
        if instance.status == 'DELIVERED':
            try:
                subject = f'Live MART: Order #{instance.order.id} - Item Delivered'
                message = (
                    f'Hi {instance.order.customer.user.username},\n\n'
                    f'Your item "{instance.inventory.product.name}" from Order #{instance.order.id} '
                    f'has been successfully delivered.\n\n'
                    f'Thank you for shopping with Live MART!'
                )
                from_email = settings.DEFAULT_FROM_EMAIL or 'noreply@livemart.com'
                recipient_list = [instance.order.customer.user.email]

                send_mail(subject, message, from_email, recipient_list)
                print(f"--- Email sent to {instance.order.customer.user.email} ---")
            except Exception as e:
                print(f"Failed to send email: {e}")


# =========================================
# === WHOLESALE-FACING VIEWS
# =========================================

class WholesaleCartItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Retailers to add, update, and remove
    items from their *wholesale* cart.
    ACCESS: Retailers only.
    """
    serializer_class = WholesaleCartItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_queryset(self):
        try:
            return WholesaleCartItem.objects.filter(cart__retailer=self.request.user.retailerprofile)
        except RetailerProfile.DoesNotExist:
            return WholesaleCartItem.objects.none()

    def create(self, request, *args, **kwargs):
        """ Custom logic for adding to wholesale cart """
        try:
            profile = request.user.retailerprofile
            cart, _ = WholesaleCart.objects.get_or_create(retailer=profile)
        except RetailerProfile.DoesNotExist:
            return Response({"error": "Retailer profile not found."}, status=status.HTTP_404_NOT_FOUND)

        inventory_id = request.data.get('inventory_id')
        quantity = int(request.data.get('quantity', 1))

        if not inventory_id:
            return Response({"error": "inventory_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retailers can ONLY buy from wholesalers
            inventory = Inventory.objects.get(
                id=inventory_id, 
                stock__gt=0,
                wholesaler__isnull=False
            )
        except Inventory.DoesNotExist:
            return Response({"error": "Wholesaler inventory item not found or is out of stock."}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item, created = WholesaleCartItem.objects.get_or_create(
            cart=cart,
            inventory=inventory,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if cart_item.quantity > inventory.stock:
            return Response(
                {"error": f"Not enough stock. Only {inventory.stock} available."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(cart_item)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK, headers=headers)


class WholesaleCartViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    API endpoint for a Retailer to view their wholesale cart
    and checkout.
    ACCESS: Retailers only.
    """
    serializer_class = WholesaleCartSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_queryset(self):
        try:
            return WholesaleCart.objects.filter(retailer=self.request.user.retailerprofile)
        except RetailerProfile.DoesNotExist:
            return Response(
                {"error": "No delivery address found. Please update your customer profile address."},
                status=status.HTTP_400_BAD_REQUEST
            )