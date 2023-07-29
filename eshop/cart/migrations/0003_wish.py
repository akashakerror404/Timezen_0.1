# Generated by Django 4.2.2 on 2023-07-16 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0006_colour_remove_products_stock_and_more"),
        ("cart", "0002_usercart_coupons"),
    ]

    operations = [
        migrations.CreateModel(
            name="Wish",
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
                ("quantity", models.PositiveIntegerField(default=1)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.productvariant",
                    ),
                ),
                (
                    "wish_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cart.usercart"
                    ),
                ),
            ],
        ),
    ]
