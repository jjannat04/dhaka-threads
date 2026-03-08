from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from store import views 
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
   openapi.Info(
      title="Dhaka Threads API",
      default_version='v1',
      description="Interactive API documentation for the Dhaka Threads Boutique",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="admin@dhakathreads.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-stats/', views.admin_dashboard, name='admin_dashboard'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   
    path('', views.home, name='home'),

    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.order_history, name='order_history'),

    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    path('api/products/', views.ProductListAPI.as_view(), name='product-list-api'),
    path('api/products/<int:pk>/', views.ProductDetailAPI.as_view(), name='product-detail-api'),
   
    path('api/products/', views.ProductListAPI.as_view(), name='product-list-api'),
    path('api/products/<int:pk>/', views.ProductDetailAPI.as_view(), name='product-detail-api'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    
    from django.views.static import serve
    from django.urls import re_path
    
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]