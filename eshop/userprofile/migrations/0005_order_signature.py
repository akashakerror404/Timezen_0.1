# Generated by Django 4.2.2 on 2023-07-11 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0004_order_payment_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="signature",
            field=models.CharField(blank=True, null=True),
        ),
    ]