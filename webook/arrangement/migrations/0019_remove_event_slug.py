# Generated by Django 3.1.1 on 2022-02-01 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0018_auto_20220113_1441'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='slug',
        ),
    ]
