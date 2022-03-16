# Generated by Django 3.1.1 on 2021-12-09 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('arrangement', '0013_auto_20211209_0722'),
    ]

    operations = [
        migrations.AddField(
            model_name='arrangement',
            name='responsible',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, related_name='arrangements_responsible_for', to='arrangement.person', verbose_name='Responsible'),
            preserve_default=False,
        ),
    ]
