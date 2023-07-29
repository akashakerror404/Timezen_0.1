from . import views
from django.urls import path

urlpatterns = [
    # path('home',views.home,name='home'),
    path('signup',views.signup, name="signup"),
    path('signin',views.signin, name="signin"),
    path('activate/<uid64>/<token>',views.activate, name="activate"),
    path('verifyotp',views.verifyotp, name="verifyotp"),
    path('logout',views.logout_view, name="logout"),
    path('forgetpassword',views.forgetpassword, name="forgetpassword"),
    path('activate_password/<uid64>/<token>',views.activate_password, name="activate_password"),
    path('reset_password',views.reset_password, name="reset_password"),




    # path('shop',views.shop, name="shop"),






]








