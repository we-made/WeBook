# Generated by Django 3.1.1 on 2023-10-17 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0092_auto_20230630_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='content',
            field=models.TextField(max_length=5000, verbose_name='Content'),
        ),
    ]
