# Generated by Django 3.1.1 on 2022-09-22 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0032_auto_20220920_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='meeting_place',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meeting Place'),
        ),
        migrations.AddField(
            model_name='event',
            name='meeting_place_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meeting Place (English)'),
        ),
    ]
