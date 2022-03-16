# Generated by Django 3.1.1 on 2022-02-18 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0026_arrangement_stages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arrangement',
            name='owners',
        ),
        migrations.AddField(
            model_name='arrangement',
            name='planners',
            field=models.ManyToManyField(to='arrangement.Person', verbose_name='Planners'),
        ),
    ]
