# Generated by Django 3.1.1 on 2022-06-10 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0006_auto_20220608_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='name_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Name English'),
        ),
    ]
