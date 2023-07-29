# Generated by Django 4.2.2 on 2023-06-26 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0003_categ_img_alter_products_available"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="products",
            name="img",
        ),
        migrations.CreateModel(
            name="product_image",
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
                ("image", models.ImageField(upload_to="products")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="store.products"
                    ),
                ),
            ],
        ),
    ]