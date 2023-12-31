"""
URL configuration for eshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from adminside import views as admin_views
from django.views.generic import TemplateView

# from django.urls import handler404

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('authentication.urls')),
    path("", include('store.urls')),
    path("", include('adminside.urls')),
    path('',include('cart.urls')),
    path('',include('userprofile.urls')),
    path('',include('coupon.urls')),
    path('404/', TemplateView.as_view(template_name='404/404.html'), name='custom_404_page'),
    path('<str:slug>/', TemplateView.as_view(template_name='404/404.html')),




    


    ]
# handler404 = 'store.views.error'

urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
