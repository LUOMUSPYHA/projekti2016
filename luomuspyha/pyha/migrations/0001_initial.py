# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_id', models.CharField(max_length=100)),
                ('count', models.IntegerField()),
                ('status', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
                ('status', models.IntegerField()),
                ('date', models.DateTimeField()),
                ('source', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=100)),
                ('approximateMatches', models.IntegerField()),
                ('downloadFormat', models.CharField(max_length=20)),
                ('downloadIncludes', models.CharField(max_length=1000)),
                ('filter_list', models.CharField(max_length=1000)),
            ],
            managers=[
                ('requests', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='collection',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyha.Request'),
        ),
    ]
