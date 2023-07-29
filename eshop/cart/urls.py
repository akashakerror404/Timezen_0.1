from django.urls import path
from . import views

urlpatterns = [
    # Existing URL patterns
 
    path('add_to_cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('delete_cart/<int:product_id>', views.delete_cart, name='delete_cart'),
    path('quantity_update/<slug>/', views.quantity_update, name='quantity_update'),

    # path('wish_list/<slug:slug>/', views.wish_list, name='wish_list'),
    path('cart/',views.cart,name='cart'),





    path('wish_list/',views.wish_list,name='wish_list'),
    path('add_to_wish/<slug:slug>/', views.add_to_wish, name='add_to_wish'),
    path('delete/<int:product_id>', views.delete, name='delete'),




   

    

    


]
