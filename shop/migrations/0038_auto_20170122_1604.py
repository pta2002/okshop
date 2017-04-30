# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-22 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0037_auto_20170121_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cached_rate',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='price_currency',
            field=models.CharField(default='OK', max_length=16),
        ),
    ]