from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Category, Product, Inventory, Feedback
from .serializers import CategorySerializer, ProductSerializer, InventorySerializer, FeedbackSerializer

# --- API Views (Store) ---
# A ViewSet automatically provides list, create, retrieve, update, delete

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

class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view all available inventory items.
    This is the main endpoint customers will browse.
    
    Provides filtering for:
    - ?product=1
    - ?retailer=1
    - ?price__gt=100 (price greater than)
    - ?price__lt=500 (price less than)
    - ?product__category=2
    - ?search=amul (searches product name)
    """
    queryset = Inventory.objects.filter(stock__gt=0) # Only show items in stock
    serializer_class = InventorySerializer
    permission_classes = [permissions.AllowAny]
    
    # --- This enables Module 3: Search & Navigation ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'product': ['exact'],
        'retailer': ['exact'],
        'price': ['gt', 'lt'],
        'product__category': ['exact'],
    }
    search_fields = ['product__name']


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reading and writing product feedback.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Must be logged in to post
    
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

