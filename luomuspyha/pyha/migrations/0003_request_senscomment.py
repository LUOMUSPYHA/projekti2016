# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-08 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0002_auto_20161206_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='sensComment',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]