# Generated by Django 4.2.2 on 2023-07-10 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0003_orderlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_id",
            field=models.CharField(blank=True, null=True),
        ),
    ]
