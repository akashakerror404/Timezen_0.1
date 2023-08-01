from django.urls import path
from . import views

urlpatterns = [
    # Existing URL patterns
    path('',views.home,name='home'),
    path('shop',views.shop,name='shop'),
    path('product_detail/<slug:slug>',views.product_detail,name='product_detail'),
    path('error',views.error,name='error'),

    


    

    


]
