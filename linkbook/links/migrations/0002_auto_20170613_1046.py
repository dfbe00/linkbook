# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-13 10:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='book',
        ),
        migrations.AddField(
            model_name='link',
            name='url',
            field=models.URLField(default=None),
        ),
    ]
