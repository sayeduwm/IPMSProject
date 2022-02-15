# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-13 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipms', '0003_auto_20160309_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriversStaff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yourstatus', models.CharField(max_length=30)),
                ('lat', models.FloatField(null=True)),
                ('lon', models.FloatField(null=True)),
                ('destination', models.CharField(max_length=30)),
                ('rdate', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(auto_now=True)),
                ('parkno', models.IntegerField(default=0)),
                ('pid', models.IntegerField(default=0)),
                ('pcost', models.FloatField(null=True)),
                ('pprice', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SpotCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yourstatus', models.CharField(max_length=30)),
            ],
        ),
    ]