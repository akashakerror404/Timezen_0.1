# Generated by Django 4.2.2 on 2023-07-15 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0005_order_signature"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="signature",
        ),
    ]
