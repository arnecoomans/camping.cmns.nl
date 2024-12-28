# Generated by Django 5.1 on 2024-12-28 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0041_size_location_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='size',
            name='display_name',
        ),
        migrations.AddField(
            model_name='size',
            name='slug',
            field=models.CharField(default='a', help_text='Slug of size', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='size',
            name='name',
            field=models.CharField(help_text='Name of size as displayed', max_length=255, unique=True),
        ),
    ]