# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-22 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0041_product_rate_lastupdated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='approved',
            field=models.BooleanField(default=True),
        ),
    ]
