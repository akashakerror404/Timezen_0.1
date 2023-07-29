from django.db import models

# Create your models here.
from store.models import *
from userprofile.models import *
from django.contrib.auth.models import User
from datetime import date  # Import the datetime module


class Coupon(models.Model):
    coupon_code= models.CharField(max_length=50,unique=True)
    discount_price=models.IntegerField(default=150)
    expiry_date = models.DateField(default=date(2023, 1, 1))  # Use the date function directly

    minimum_amount=models.IntegerField(default=500)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_code
    def check_expiry_status(self):
        if self.expiry_date < date.today():
            self.is_expired = True
        else:
            self.is_expired = False




class Usercoupon(models.Model):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)
    total_price=models.IntegerField(null=True)


class ReferralProgram(models.Model):
    description = models.TextField(blank=True,null=True)
    userwallet=models.IntegerField(default=50)
    referrerdwallet=models.IntegerField(default=100)

    def __str__(self):
        return f"{self.userwallet}-{self.referrerdwallet}"
