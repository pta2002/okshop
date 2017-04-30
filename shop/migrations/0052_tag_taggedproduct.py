# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 17:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0051_review_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('nsfw', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TaggedProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Product')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Tag')),
            ],
        ),
    ]