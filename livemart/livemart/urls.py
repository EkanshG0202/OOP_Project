from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# --- Import our ViewSets ---
from store.views import CategoryViewSet, ProductViewSet, InventoryViewSet, FeedbackViewSet
from orders.views import CartViewSet, OrderViewSet

# --- API URL Routing ---
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- API URLs ---
    path('api/', include(router.urls)), # Our new API endpoints
    
    # --- Authentication URLs ---
    # Provides /api/auth/login/, /api/auth/logout/, /api/auth/password/reset/
    path('api/auth/', include('dj_rest_auth.urls')),
    # Provides /api/auth/registration/
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]

# Add URL pattern for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

