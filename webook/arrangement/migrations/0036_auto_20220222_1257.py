# Generated by Django 3.1.1 on 2022-02-22 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0035_auto_20220222_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderedservice',
            name='confirmation_receipt',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.RESTRICT, related_name='ordered_service', to='arrangement.confirmationreceipt'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderedservice',
            name='order_information',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='orderedservice',
            name='provider',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.RESTRICT, related_name='ordered_services', to='arrangement.serviceprovidable'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderedservice',
            name='state',
            field=models.CharField(choices=[('awaiting_response', 'awaiting_response'), ('denied', 'denied'), ('accepted', 'accepted'), ('cancelled', 'cancelled')], default='awaiting_response', max_length=255),
        ),
        migrations.AlterField(
            model_name='collisionanalysisrecord',
            name='collided_with_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collision_records_bystanded', to='arrangement.event'),
        ),
    ]
