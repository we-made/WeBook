# Generated by Django 3.1.1 on 2022-11-11 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0044_auto_20221111_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_resolution',
            field=models.BooleanField(default=False, verbose_name='Is the result of a collision resolution'),
        ),
    ]
