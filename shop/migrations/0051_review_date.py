# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-10 23:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0050_auto_20170210_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]