from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import *
from coupon.models import *



# Create your models here.
class UserCart(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    coupons = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null=True, blank=True )

    def __str__(self):
        return f'{self.id} - {self.user.username}'

@receiver(post_save,sender=User)
def create_user_cart(sender,instance,created,**kwargs):
    if created:
        UserCart.objects.create(user=instance)



class Cart(models.Model):
    cart_id = models.ForeignKey(UserCart,on_delete=models.CASCADE)
    product=models.ForeignKey(productVariant,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.id} - {self.cart_id} - {self.product}'

    def total_price(self):
        return self.quantity *self.price

class UserWish(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} - {self.user.username}'

@receiver(post_save,sender=User)
def create_user_wish(sender,instance,created,**kwargs):
    if created:
        UserWish.objects.create(user=instance)


class Wish(models.Model):
    wish_id=models.ForeignKey(UserWish,on_delete=models.CASCADE)
    product=models.ForeignKey(productVariant,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f'{self.id} - {self.wish_id} - {self.product}'
    def total_price(self):
        return self.quantity *self.price








class Wallet(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    Wallettotal=models.IntegerField(null=True,blank=True,default=0)

    def Wallet_total(self):
        return f"{self.user.username}'s wallet:{self.Wallettotal}"
