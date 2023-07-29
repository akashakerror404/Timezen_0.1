from django.db import models

# Create your models here.
from django.contrib.auth.models import User
import string
import random


# Create your models here.

def generate_referral_code():
    # Implement a function to generate a unique referral code
    code_length = 6
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(code_length))


class Referral(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10, unique=True)
    referred_by = models.ForeignKey(User, related_name='referrals', null=True, blank=True, on_delete=models.SET_NULL)
    

    def str(self):
        return f"{self.user.username}'s Referral: {self.referral_code} Referred: {self.referred_by} "