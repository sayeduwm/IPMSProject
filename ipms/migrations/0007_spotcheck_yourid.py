# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-14 04:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipms', '0006_student_instant_studentinstant'),
    ]

    operations = [
        migrations.AddField(
            model_name='spotcheck',
            name='yourid',
            field=models.IntegerField(default=0),
        ),
    ]