from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# --- Import our ViewSets ---
from store.views import CategoryViewSet, ProductViewSet, InventoryViewSet, FeedbackViewSet

# --- UPDATED: Import all ViewSets from orders.views ---
from orders.views import (
    CartViewSet, 
    OrderViewSet, 
    CartItemViewSet,
    RetailerOrderViewSet, 
    RetailerOrderItemViewSet,
    WholesaleCartItemViewSet, 
    WholesaleCartViewSet, 
    WholesaleOrderViewSet,
    WholesalerFulfillmentViewSet # --- IMPORTED ---
)

# --- API URL Routing ---
router = DefaultRouter()

# Store App
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

# Orders App (Customer)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')

# Orders App (Retailer-facing)
router.register(r'retailer/orders', RetailerOrderViewSet, basename='retailer-order')
router.register(r'retailer/order-items', RetailerOrderItemViewSet, basename='retailer-orderitem')

# Orders App (Wholesale system)
router.register(r'wholesale-cart-items', WholesaleCartItemViewSet, basename='wholesale-cartitem')
router.register(r'wholesale-cart', WholesaleCartViewSet, basename='wholesale-cart')
router.register(r'wholesale-orders', WholesaleOrderViewSet, basename='wholesale-order')

# --- ADDED: Orders App (Wholesaler-facing) ---
router.register(r'wholesaler/order-items', WholesalerFulfillmentViewSet, basename='wholesaler-orderitem')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- API URLs ---
    path('api/', include(router.urls)), 
    
    # --- Authentication URLs ---
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)