# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-12-10 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observe', '0017_auto_20180621_0756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asteroid',
            name='image_url',
            field=models.CharField(default='https://lco.global/files/astronomy/asteroid/unknown.jpg', max_length=200),
        ),
        migrations.AlterField(
            model_name='asteroid',
            name='timelapse_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
