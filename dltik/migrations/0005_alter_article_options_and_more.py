# Generated by Django 5.2.1 on 2025-06-08 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dltik', '0004_page_format'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['-created_at']},
        ),
        migrations.RenameField(
            model_name='article',
            old_name='published_at',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='article',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='format',
            field=models.CharField(choices=[('html', 'HTML'), ('text', 'Plain Text'), ('json', 'JSON'), ('js', 'JavaScript'), ('xml', 'XML'), ('md', 'Markdown'), ('csv', 'CSV'), ('rss', 'RSS'), ('yaml', 'YAML'), ('ini', 'INI'), ('custom', 'Custom Text')], default='html', max_length=10),
        ),
    ]
