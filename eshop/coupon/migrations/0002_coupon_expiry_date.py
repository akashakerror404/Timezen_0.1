# Generated by Django 4.2.2 on 2023-07-17 11:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coupon", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="coupon",
            name="expiry_date",
            field=models.DateField(default=datetime.date(2023, 1, 1)),
        ),
    ]