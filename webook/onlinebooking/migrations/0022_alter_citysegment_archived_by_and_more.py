# Generated by Django 4.2.10 on 2024-10-23 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # ('arrangement', '0056_alter_arrangement_archived_by_and_more'),
        ("onlinebooking", "0021_alter_onlinebookingsettings_audience_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="citysegment",
            name="archived_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="%(class)s_archived_by",
                to="arrangement.person",
                verbose_name="Archived by",
            ),
        ),
        migrations.AlterField(
            model_name="county",
            name="archived_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="%(class)s_archived_by",
                to="arrangement.person",
                verbose_name="Archived by",
            ),
        ),
        migrations.AlterField(
            model_name="onlinebooking",
            name="archived_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="%(class)s_archived_by",
                to="arrangement.person",
                verbose_name="Archived by",
            ),
        ),
        migrations.AlterField(
            model_name="school",
            name="archived_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="%(class)s_archived_by",
                to="arrangement.person",
                verbose_name="Archived by",
            ),
        ),
    ]
