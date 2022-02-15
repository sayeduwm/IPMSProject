# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-08 17:23
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.IntegerField()),
                ('width', models.IntegerField()),
                ('precision', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipms.Attribute')),
            ],
        ),
        migrations.CreateModel(
            name='BaseMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Drivers',
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
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geom_point', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('geom_multipoint', django.contrib.gis.db.models.fields.MultiPointField(blank=True, null=True, srid=4326)),
                ('geom_multilinestring', django.contrib.gis.db.models.fields.MultiLineStringField(blank=True, null=True, srid=4326)),
                ('geom_multipolygon', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326)),
                ('geom_geometrycollection', django.contrib.gis.db.models.fields.GeometryCollectionField(blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Parkinglot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('park_use', models.CharField(blank=True, max_length=20, null=True)),
                ('park_no', models.IntegerField()),
                ('xcord', models.FloatField()),
                ('ycord', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Parkingspot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=2, null=True)),
                ('pid', models.IntegerField()),
                ('id_sub', models.CharField(blank=True, max_length=2, null=True)),
                ('park_use', models.CharField(blank=True, max_length=20, null=True)),
                ('park_no', models.IntegerField()),
                ('park_name', models.CharField(blank=True, max_length=50, null=True)),
                ('level', models.IntegerField()),
                ('address', models.CharField(blank=True, max_length=50, null=True)),
                ('una', models.FloatField()),
                ('powers_hal', models.FloatField()),
                ('wesleyan_h', models.FloatField()),
                ('mathematic', models.FloatField()),
                ('collier_li', models.FloatField()),
                ('commons', models.FloatField()),
                ('guc', models.FloatField()),
                ('science', models.FloatField()),
                ('art_build', models.FloatField()),
                ('floyd_hall', models.FloatField()),
                ('music_buil', models.FloatField()),
                ('willingham', models.FloatField()),
                ('stevens_ha', models.FloatField(null=True)),
                ('bibb_grave', models.FloatField()),
                ('kellerhall', models.FloatField()),
                ('status', models.IntegerField()),
                ('xcord', models.FloatField()),
                ('ycord', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Shapefile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('srs_wkt', models.TextField(max_length=1000)),
                ('geom_type', models.CharField(max_length=50)),
                ('encoding', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Stopage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=2, null=True)),
                ('sid', models.IntegerField()),
                ('stop', models.CharField(blank=True, max_length=50, null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
        ),
        migrations.AddField(
            model_name='feature',
            name='shapefile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipms.Shapefile'),
        ),
        migrations.AddField(
            model_name='attributevalue',
            name='feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipms.Feature'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='shapefile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipms.Shapefile'),
        ),
    ]