# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-07 15:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observe', '0002_auto_20160607_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='asteroid',
            name='image',
            field=models.TextField(default='no-image.jpg'),
        ),
        migrations.AddField(
            model_name='asteroid',
            name='teaser',
            field=models.CharField(default='this is interesting', max_length=120),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asteroid',
            name='end',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 7, 15, 51, 42, 4409)),
        ),
        migrations.AlterField(
            model_name='asteroid',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 7, 15, 51, 42, 4168)),
        ),
    ]