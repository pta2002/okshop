# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-17 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0033_shippingupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingupdate',
            name='short_update',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
