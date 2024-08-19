# Generated by Django 3.2 on 2024-07-15 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinebooking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='city_segment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='schools_in_segment', to='onlinebooking.citysegment'),
        ),
        migrations.AlterField(
            model_name='school',
            name='county',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='schools_in_county', to='onlinebooking.county'),
        ),
    ]
