# Generated by Django 3.1.1 on 2022-02-24 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0041_looseservicerequisition_generated_requisition_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='requisitionrecord',
            name='arrangement',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.RESTRICT, related_name='requisitions', to='arrangement.arrangement'),
            preserve_default=False,
        ),
    ]
