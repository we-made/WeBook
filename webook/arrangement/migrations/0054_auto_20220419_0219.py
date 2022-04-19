# Generated by Django 3.1.1 on 2022-04-19 02:19

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('screenshow', '0002_auto_20220419_0219'),
        ('arrangement', '0053_event_title_en'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArrangementFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('file', models.FileField(upload_to='arrangementFiles/')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='screengroup',
            name='screens',
        ),
        migrations.RemoveField(
            model_name='screenresource',
            name='location',
        ),
        migrations.RemoveField(
            model_name='screenresource',
            name='screen_groups',
        ),
        migrations.AddField(
            model_name='arrangement',
            name='actual_visitors',
            field=models.IntegerField(default=0, verbose_name='Actual visitors'),
        ),
        migrations.AddField(
            model_name='arrangement',
            name='expected_visitors',
            field=models.IntegerField(default=0, verbose_name='Expected visitors'),
        ),
        migrations.AddField(
            model_name='arrangement',
            name='meeting_place',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meeting Place'),
        ),
        migrations.AddField(
            model_name='arrangement',
            name='ticket_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ticket Code'),
        ),
        migrations.AddField(
            model_name='event',
            name='actual_visitors',
            field=models.IntegerField(default=0, verbose_name='Actual visitors'),
        ),
        migrations.AddField(
            model_name='event',
            name='expected_visitors',
            field=models.IntegerField(default=0, verbose_name='Expected visitors'),
        ),
        migrations.AddField(
            model_name='event',
            name='ticket_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ticket Code'),
        ),
        migrations.AddField(
            model_name='room',
            name='is_exclusive',
            field=models.BooleanField(default=False, verbose_name='Is Exclusive'),
        ),
        migrations.AlterField(
            model_name='arrangement',
            name='display_layouts',
            field=models.ManyToManyField(related_name='arrangements', to='screenshow.DisplayLayout', verbose_name='Display Layout'),
        ),
        migrations.AlterField(
            model_name='event',
            name='display_layouts',
            field=models.ManyToManyField(related_name='events', to='screenshow.DisplayLayout', verbose_name='Display Layouts'),
        ),
        migrations.DeleteModel(
            name='DisplayLayout',
        ),
        migrations.DeleteModel(
            name='DisplayLayoutSetting',
        ),
        migrations.DeleteModel(
            name='ScreenGroup',
        ),
        migrations.DeleteModel(
            name='ScreenResource',
        ),
        migrations.AddField(
            model_name='arrangementfile',
            name='arrangement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='files', to='arrangement.arrangement'),
        ),
        migrations.AddField(
            model_name='arrangementfile',
            name='uploader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='files_uploaded_to_arrangements', to='arrangement.person'),
        ),
    ]
