# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-09 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyha', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='downloadRequestHandler',
            field=models.CharField(max_length=500, null=True),
        ),
    ]