from django.urls import path
from . import views

urlpatterns = [
    # Existing URL patterns
 



    path('adress_selection',views.adress_selection,name='adress_selection'),

    path('add_address',views.add_address,name='add_address'),

    path('edit_address/<int:address_id>', views.edit_address, name='edit_address'),
    
    path('place_order/<int:address_id>', views.place_order, name='place_order'),

    path('order_placed/<int:address_id>', views.order_placed, name='order_placed'),

    path('userprofile',views.userprofile,name='userprofile'),

    path('user_orders_list',views.user_orders_list,name='user_orders_list'),

    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),

    path('order/<int:order_id>/', views.view_order_details, name='view_order_details'),

    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),

    path('order_placed_razopay/<int:address_id>', views.order_placed_razopay, name='order_placed_razopay'),

    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('wallet',views.wallet,name='wallet'),

    path('refund_method/<int:order_id>/', views.refund_method, name='refund_method'),

    path('order_wallet/<int:address_id>', views.order_wallet, name='order_wallet'),

    path('update_profile/',views.update_profile,name='update_profile'),

    path('help',views.help,name='help'),



    # path('update_order_status_user/<int:order_id>/', views.update_order_status_user, name='update_order_status_user'),
















    



   

    

    


]
