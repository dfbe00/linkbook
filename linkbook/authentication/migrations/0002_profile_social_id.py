# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-21 09:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='social_id',
            field=models.CharField(default=123, max_length=50),
            preserve_default=False,
        ),
    ]
