# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-28 19:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='open',
            field=models.BooleanField(default=True),
        ),
    ]
