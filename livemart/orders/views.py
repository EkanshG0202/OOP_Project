from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django.db import transaction

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from users.models import CustomerProfile
from store.models import Inventory # We need this for checkout

# --- PHASE 5: Cart Item Management ---

class CartItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for adding, updating, and removing items
    from the user's cart.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see and manage their own cart items.
        """
        try:
            return CartItem.objects.filter(cart__customer__user=self.request.user)
        except CustomerProfile.DoesNotExist:
            return CartItem.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Custom logic for adding an item to the cart.
        If the item is already in the cart, we just update the quantity.
        """
        try:
            profile = request.user.customerprofile
            cart, _ = Cart.objects.get_or_create(customer=profile)
        except CustomerProfile.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        inventory_id = serializer.validated_data['inventory_id']
        quantity = serializer.validated_data['quantity']

        try:
            inventory = Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if item is in stock
        if inventory.stock < quantity:
            return Response({"error": f"Not enough stock for {inventory.product.name}. Only {inventory.stock} left."}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            inventory=inventory,
            defaults={'quantity': quantity}
        )

        if not created:
            # If item already in cart, update quantity
            total_quantity = cart_item.quantity + quantity
            if inventory.stock < total_quantity:
                return Response({"error": f"Not enough stock. You already have {cart_item.quantity} in cart and stock is {inventory.stock}."}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = total_quantity
            cart_item.save()
            serializer = self.get_serializer(cart_item) # Reserialize with updated data
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CartViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for retrieving the user's shopping cart.
    (This is unchanged from before, but kept for clarity)
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            profile = self.request.user.customerprofile
            return Cart.objects.filter(customer=profile)
        except CustomerProfile.DoesNotExist:
            return Cart.objects.none()

    def get_object(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        cart, _ = Cart.objects.get_or_create(customer=profile)
        return cart

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# --- PHASE 5: Transactional Checkout Logic ---

class OrderViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for placing and viewing orders.
    'list' = get all my orders
    'retrieve' = get one specific order
    'create' = place a new order (THE CHECKOUT)
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            return Order.objects.filter(customer=self.request.user.customerprofile).order_by('-created_at')
        except CustomerProfile.DoesNotExist:
            return Order.objects.none()

    def perform_create(self, serializer):
        """
        This is the main "Checkout" logic.
        We override this method to run our transactional checkout.
        """
        try:
            profile = self.request.user.customerprofile
            cart = profile.cart
        except (CustomerProfile.DoesNotExist, Cart.DoesNotExist):
            raise ValidationError("User profile or cart not found.")

        cart_items = cart.items.all()
        if not cart_items.exists():
            raise ValidationError("Your cart is empty.")

        total_price = 0
        order_items_to_create = []

        try:
            # --- START DATABASE TRANSACTION ---
            # This ensures that if *any* part of the checkout fails
            # (e.g., one item is out of stock), the *entire*
            # transaction is rolled back. No partial orders.
            with transaction.atomic():
                
                # 1. Save the Order instance first
                # The serializer already validated shipping_address, etc.
                order = serializer.save(
                    customer=profile,
                    total_price=0 # We will calculate and update this
                )

                # 2. Loop through cart items, check stock, and prepare OrderItems
                for item in cart_items:
                    
                    # --- CRITICAL: Lock the inventory row ---
                    # This prevents race conditions, e.g., two users
                    # buying the last item at the exact same time.
                    try:
                        inventory = Inventory.objects.select_for_update().get(id=item.inventory.id)
                    except Inventory.DoesNotExist:
                        raise ValidationError(f"Item {item.inventory.product.name} is no longer available.")

                    # 3. Check stock
                    if inventory.stock < item.quantity:
                        raise ValidationError(f"Not enough stock for {inventory.product.name}. Only {inventory.stock} left.")

                    # 4. Decrement stock
                    inventory.stock -= item.quantity
                    inventory.save()

                    # 5. Calculate price and add to total
                    price_at_purchase = inventory.price
                    total_price += (price_at_purchase * item.quantity)
                    
                    # 6. Prepare the OrderItem to be created
                    order_items_to_create.append(
                        OrderItem(
                            order=order,
                            inventory=inventory,
                            quantity=item.quantity,
                            price_at_purchase=price_at_purchase
                        )
                    )

                # 7. Update the order's total price
                order.total_price = total_price
                order.save()

                # 8. Bulk create all OrderItems in one efficient query
                OrderItem.objects.bulk_create(order_items_to_create)

                # 9. Clear the user's cart
                cart.items.all().delete()

            # --- END DATABASE TRANSACTION ---
            
        except ValidationError as e:
            # If we raised a stock error, reraise it
            raise e
        except Exception as e:
            # Catch any other unexpected errors
            raise ValidationError(f"An error occurred during checkout: {str(e)}")

