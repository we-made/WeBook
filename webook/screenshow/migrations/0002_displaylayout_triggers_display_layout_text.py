# Generated by Django 3.1.1 on 2022-09-26 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screenshow', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='displaylayout',
            name='triggers_display_layout_text',
            field=models.BooleanField(default=False, verbose_name='Triggers Display Layout Text Fields'),
        ),
    ]
