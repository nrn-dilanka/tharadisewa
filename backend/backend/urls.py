"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from user.test_views import test_connection, health_check, list_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include('user.auth_urls')),
    path("api/test-connection/", test_connection, name='api_test_connection'),
    path("api/health/", health_check, name='api_health_check'),
    path("api/debug/urls/", list_urls, name='api_debug_urls'),
    path("api/", include('user.urls')),
    path("api/", include('customer.urls')),
    path("api/", include('customer_contact.urls')),
    path("api/", include('shop.urls')),
    path("api/", include('location.urls')),
    path("api/", include('product.urls')),
    path("api/", include('purchase.urls')),
    path("api/", include('services.urls')),
    path("api/", include('bill.urls')),
    path("api/", include('Technical.urls')),
    path("api/", include('Rapair.urls')),
    path("api/", include('license.urls')),
]
