from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# --- Import our ViewSets ---
from store.views import CategoryViewSet, ProductViewSet, InventoryViewSet, FeedbackViewSet
from orders.views import CartViewSet, OrderViewSet, CartItemViewSet 
# --- 1. IMPORT YOUR NEW VIEW ---
from users.views import CustomRegistrationView

# --- API URL Routing ---
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- API URLs ---
    path('api/', include(router.urls)), 
    
    # --- Authentication URLs ---
    path('api/auth/', include('dj_rest_auth.urls')),
    
    # --- 2. REPLACE THE DEFAULT REGISTRATION URL ---
    # This line is the fix. It points to your custom view.
    path(
        'api/auth/registration/', 
        CustomRegistrationView.as_view(), 
        name='custom_register'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)