# Generated by Django 5.2.1 on 2025-06-08 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dltik', '0002_rename_download_count_file_downloads'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='format',
        ),
        migrations.RemoveField(
            model_name='page',
            name='slug',
        ),
        migrations.AddField(
            model_name='page',
            name='path',
            field=models.CharField(default='temp', max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
