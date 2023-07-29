# Generated by Django 4.2.2 on 2023-06-26 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_alter_products_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="categ",
            name="img",
            field=models.ImageField(blank=True, null=True, upload_to="categ"),
        ),
        migrations.AlterField(
            model_name="products",
            name="available",
            field=models.BooleanField(default=True),
        ),
    ]
