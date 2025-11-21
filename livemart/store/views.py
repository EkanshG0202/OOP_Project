from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Inventory, Feedback
from users.models import RetailerProfile
from .serializers import (
    CategorySerializer, 
    ProductSerializer, 
    InventorySerializer, 
    FeedbackSerializer,
    RetailerListSerializer 
)

# --- Import geopy for distance calculation ---
from geopy.distance import geodesic
# ---------------------------------------------

from users.permissions import IsCustomer, IsSeller, IsOwnerOfInventory, IsOwnerOfFeedbackOrReadOnly

# --- API Views (Store) ---

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view product categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_region_specific']
    search_fields = ['name', 'description']

class InventoryViewSet(viewsets.ModelViewSet): 
    """
    API endpoint to view and manage inventory.
    - Supports standard filtering (price, product name).
    - Supports LOCATION filtering: ?lat=28.7&lon=77.1&radius=5
    """
    serializer_class = InventorySerializer
    
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
        Standard queryset logic + Distance Filtering.
        """
        user = self.request.user
        queryset = Inventory.objects.all()
        
        # 1. Role-based Base Filtering
        if user.is_authenticated and user.role in ['RETAILER', 'WHOLESALER']:
            if user.role == 'RETAILER':
                queryset = Inventory.objects.filter(retailer=user.retailerprofile)
            else: # Wholesaler
                queryset = Inventory.objects.filter(wholesaler=user.wholesalerprofile)
        else:
            # For customers/anonymous: Only show in-stock items
            queryset = Inventory.objects.filter(stock__gt=0)

        # 2. Location-based Filtering (The New Feature)
        user_lat = self.request.query_params.get('lat')
        user_lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius')

        if user_lat and user_lon and radius:
            try:
                user_coords = (float(user_lat), float(user_lon))
                radius_km = float(radius)
                
                # We must filter in Python because SQLite doesn't support geo-math
                nearby_ids = []
                
                for item in queryset:
                    # We currently only filter Retailer inventory by location
                    # (Wholesalers don't have lat/lon columns yet)
                    if item.retailer and item.retailer.location_lat and item.retailer.location_lon:
                        shop_coords = (item.retailer.location_lat, item.retailer.location_lon)
                        
                        distance = geodesic(user_coords, shop_coords).km
                        
                        if distance <= radius_km:
                            nearby_ids.append(item.id)
                
                # Return only the items that passed the distance check
                queryset = queryset.filter(id__in=nearby_ids)
                
            except ValueError:
                pass # If params are invalid, ignore location filter

        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsSeller]
        else: 
            permission_classes = [permissions.IsAuthenticated, IsSeller, IsOwnerOfInventory]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'RETAILER':
            serializer.save(retailer=user.retailerprofile)
        elif user.role == 'WHOLESALER':
            serializer.save(wholesaler=user.wholesalerprofile)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reading and writing product feedback.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsCustomer]
        else: 
            permission_classes = [permissions.IsAuthenticated, IsOwnerOfFeedbackOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class RetailerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API to list shops.
    Supports location filtering: ?lat=12.34&lon=56.78&radius=10
    """
    serializer_class = RetailerListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return RetailerProfile.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        user_lat = request.query_params.get('lat')
        user_lon = request.query_params.get('lon')
        radius = float(request.query_params.get('radius', 50)) 
        
        if not user_lat or not user_lon:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        try:
            user_coords = (float(user_lat), float(user_lon))
        except ValueError:
             return Response({"error": "Invalid lat/lon format"}, status=400)

        nearby_retailers = []
        
        for retailer in queryset:
            if retailer.location_lat and retailer.location_lon:
                shop_coords = (retailer.location_lat, retailer.location_lon)
                distance = geodesic(user_coords, shop_coords).km
                
                if distance <= radius:
                    retailer.distance_km = round(distance, 2)
                    nearby_retailers.append(retailer)

        nearby_retailers.sort(key=lambda x: x.distance_km)

        page = self.paginate_queryset(nearby_retailers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(nearby_retailers, many=True)
        return Response(serializer.data)