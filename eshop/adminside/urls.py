from django.urls import path
from . import views

urlpatterns = [
    # Existing URL patterns
    path('adminside',views.admin,name='adminside'),
    path('usertable',views.usertable,name='usertable'),
    path('category',views.category,name='category'),
    path('block_user/<int:user_id>/',views.block_user,name='block_user'),
    path('unblock_user/<int:user_id>/',views.unblock_user,name='unblock_user'),
    path('add_product/', views.add_product, name='add_product'),
    path('logoutadmin',views.logoutadmin, name="logoutadmin"),
    path('dashboard',views.dashboard, name="dashboard"),
    path('add_categ',views.add_categ, name="add_categ"),
    path('viewproduct/<int:product_id>/', views.viewproduct, name='viewproduct'),
    path('admin_order_list', views.admin_order_list, name='admin_order_list'),
    path('order_details_admin/<int:order_id>/', views.order_details_admin, name='order_details_admin'),
    path('cancel_order_admin/<int:order_id>/', views.cancel_order_admin, name='cancel_order_admin'),
    path('add_variant/<int:product_id>/', views.add_variant, name='add_variant'),
    path('order/download/<int:order_id>/', views.download_order_pdf, name='download_order_pdf'),
    path('download_order_pdf2/<int:order_id>/', views.download_order_pdf2, name='download_order_pdf2'),
    path('edit_variant/<int:variant_id>/', views.edit_variant, name='edit_variant'),
    path('product_management', views.product_management, name='product_management'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('soft_delete_product/<slug:slug>/', views.soft_delete_product, name='soft_delete_product'),
    path('undo_soft_delete_product/<slug:slug>/', views.undo_soft_delete_product, name='undo_soft_delete_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='editproduct'),
    path('update_order_status_admin/<int:order_id>/', views.update_order_status_admin, name='update_order_status_admin'),
    path('download_order_pdf_sales', views.download_order_pdf_sales, name='download_order_pdf_sales'),
    path('create_coupons', views.create_coupon, name='create_coupons'),
    path('add_color/', views.add_color, name='add_color'),
    path('add_referral_program/', views.add_referral_program, name='add_referral_program'),
    path('edit_referral_program/<int:program_id>/', views.edit_referral_program, name='edit_referral_program'),
    path('return_order_list/', views.return_order_list, name='return_order_list'),
    path('refund_admin/<int:order_id>/', views.refund_admin, name='refund_admin'),
    path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('banner',views.banner,name='banner'),
    path('delete_image/<int:image_id>/', views.delete_image, name='delete_image'),



















   

    

    


]
