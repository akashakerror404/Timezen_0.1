# Generated by Django 4.2.2 on 2023-07-15 06:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("coupon_code", models.CharField(max_length=50, unique=True)),
                ("discount_price", models.IntegerField(default=150)),
                ("minimum_amount", models.IntegerField(default=500)),
                ("is_expired", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Usercoupon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_price", models.IntegerField(null=True)),
                (
                    "coupon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="coupon.coupon"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
