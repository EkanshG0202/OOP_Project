from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# --- Import ViewSets from Store ---
from store.views import (
    CategoryViewSet, 
    ProductViewSet, 
    InventoryViewSet, 
    FeedbackViewSet,
    RetailerViewSet # <--- ADDED for Location Feature
)

# --- Import ViewSets from Orders ---
from orders.views import (
    CartViewSet, 
    OrderViewSet, 
    CartItemViewSet,
    RetailerOrderViewSet,       # <--- Restored
    RetailerOrderItemViewSet,   # <--- Restored
    WholesaleCartItemViewSet,   # <--- Restored
    WholesaleCartViewSet,       # <--- Restored
    WholesaleOrderViewSet,      # <--- Restored
    WholesalerFulfillmentViewSet # <--- Restored
)

# --- Import Views from Users ---
from users.views import GoogleLogin # <--- ADDED for Social Login

# --- API URL Routing ---
router = DefaultRouter()

# Store App
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'shops', RetailerViewSet, basename='shop') # <--- ADDED: Shops Near Me

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

# Orders App (Wholesaler-facing)
router.register(r'wholesaler/order-items', WholesalerFulfillmentViewSet, basename='wholesaler-orderitem')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- API URLs ---
    path('api/', include(router.urls)), 
    
    # --- Authentication URLs ---
    path('api/auth/', include('dj_rest_auth.urls')),
    
    # Registration (Uses your CustomRegisterSerializer from settings.py)
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # --- Social Login URL ---
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)