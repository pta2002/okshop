# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-15 13:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0023_auto_20170115_1321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usershop',
            old_name='customcss',
            new_name='custom_css',
        ),
    ]
