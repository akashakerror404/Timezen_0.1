


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from store.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver




# Create your models here.

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50,blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=50,blank=True)
    country = models.CharField(max_length=50,blank=True)
    state = models.CharField(max_length=50,blank=True)
    city = models.CharField(max_length=50,blank=True)
    pincode = models.CharField(max_length=50,blank=True)

    def __str__(self):
        return f"{self.id}"


class Order(models.Model):
    PAYMENT_STATUS_CHOICE = [
        ('PENDING','Pending'),
        ('PAID','Paid'),
        ('CANCELLED','Cancelled'),
        ('DELIVERED','Delivered'),
        ('SHIPPED','shipped'),
        ('ORDERED','ordered'),
        ('RETURN','return'),
        ('REFUND','refund'),


        
    ]

    PAYMENT_METHOD_CHOICES=[
        ('PREPAID','PREPAID'),
        ('CASH_ON_DELIVERY','Cash on Delivery'),
        ('WALLET','wallet'),

    ]

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    address=models.ForeignKey(Address,on_delete=models.CASCADE)
    order_date=models.DateTimeField(default=timezone.now)
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    payment_status=models.CharField(max_length=20,choices=PAYMENT_STATUS_CHOICE,default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    delivery_date=models.DateTimeField(blank=True,null=True)
    payment_id=models.CharField(blank=True,null=True)

    def __str__(self):
        return f"{self.id} {self.user.username}"

    def save(self,*args,**kwargs):
        if not self.order_date:
            self.order_date=timezone.now()

        if not self.delivery_date:
            self.delivery_date = self.order_date + timedelta(hours=24)
        super().save(*args,**kwargs)

class Orderlist(models.Model):
    order_id=models.ForeignKey(Order,on_delete=models.CASCADE)
    product=models.ForeignKey(productVariant,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return f'{self.order_id}{self.product.products.name}'
class PersonalDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phonenumber=models.CharField(blank=True,null=True)

    @receiver(post_save,sender=User)
    def create_PerosnalDetails(sender,instance,created,**kwargs):
        if created:
            PersonalDetails.objects.create(user=instance)
