# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-25 19:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipms', '0008_leavespot'),
    ]

    operations = [
        migrations.AddField(
            model_name='drivers',
            name='pin',
            field=models.CharField(default=0, max_length=30),
        ),
        migrations.AddField(
            model_name='driversstaff',
            name='pin',
            field=models.CharField(default=0, max_length=30),
        ),
        migrations.AddField(
            model_name='requesttest',
            name='pin',
            field=models.CharField(default=0, max_length=30),
        ),
        migrations.AddField(
            model_name='studentinstant',
            name='pin',
            field=models.CharField(default=0, max_length=30),
        ),
    ]
