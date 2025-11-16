from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Inventory, Feedback
from .serializers import CategorySerializer, ProductSerializer, InventorySerializer, FeedbackSerializer

# --- Import our new custom permissions ---
from users.permissions import IsCustomer, IsSeller, IsOwnerOfInventory, IsOwnerOfFeedbackOrReadOnly

# --- API Views (Store) ---

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view product categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Everyone can see categories

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_region_specific'] # Filter by ?category=1
    search_fields = ['name', 'description'] # Search by ?search=milk

class InventoryViewSet(viewsets.ModelViewSet): # <-- CHANGED from ReadOnlyModelViewSet
    """
    API endpoint to view and manage inventory.
    - ALL users can list and retrieve (read).
    - SELLERS (Retailer/Wholesaler) can create inventory.
    - The OWNER of an inventory item can update or delete it.
    """
    serializer_class = InventorySerializer
    
    # --- This enables Module 3: Search & Navigation ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'product': ['exact'],
        'retailer': ['exact'],
        'price': ['gt', 'lt'],
        'product__category': ['exact'],
    }
    search_fields = ['product__name']

    def get_queryset(self):
        """
        - Customers/Anonymous users see all *in-stock* items.
        - A Seller (Retailer/Wholesaler) sees *all* of their own items,
          including out-of-stock items, so they can manage them.
        """
        user = self.request.user
        
        if user.is_authenticated and user.role in ['RETAILER', 'WHOLESALER']:
            if user.role == 'RETAILER':
                return Inventory.objects.filter(retailer=user.retailerprofile)
            else: # Wholesaler
                return Inventory.objects.filter(wholesaler=user.wholesalerprofile)
        
        # For customers or anonymous users
        return Inventory.objects.filter(stock__gt=0)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - list, retrieve: AllowAny
        - create: IsAuthenticated, IsSeller
        - update, destroy: IsAuthenticated, IsSeller, IsOwnerOfInventory
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsSeller]
        else: # 'update', 'partial_update', 'destroy'
            permission_classes = [permissions.IsAuthenticated, IsSeller, IsOwnerOfInventory]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Automatically link new inventory to the logged-in seller.
        The 'product' is set via 'product_id' in the serializer.
        """
        user = self.request.user
        if user.role == 'RETAILER':
            serializer.save(retailer=user.retailerprofile)
        elif user.role == 'WHOLESALER':
            serializer.save(wholesaler=user.wholesalerprofile)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reading and writing product feedback.
    - ALL users can read feedback.
    - CUSTOMERS can create feedback.
    - The OWNER of feedback can update or delete it.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - list, retrieve: AllowAny
        - create: IsAuthenticated, IsCustomer
        - update, destroy: IsAuthenticated, IsCustomer, IsOwnerOfFeedbackOrReadOnly
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsCustomer]
        else: # 'update', 'partial_update', 'destroy'
            permission_classes = [permissions.IsAuthenticated, IsOwnerOfFeedbackOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Allow filtering feedback by product
        # e.g., /api/feedback/?product=1
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        # Automatically set the customer to the logged-in user
        serializer.save(customer=self.request.user)