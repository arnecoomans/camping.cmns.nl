# Generated by Django 5.1 on 2024-09-01 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0028_profile_show_category_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='primary',
            field=models.BooleanField(default=False, help_text='primary link for location'),
        ),
    ]
