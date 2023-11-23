# Generated by Django 4.2.6 on 2023-11-22 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0018_profile_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='order',
            field=models.CharField(choices=[('distance', 'distance'), ('region', 'region'), ('date_added', 'date added'), ('date_modified', 'date modified')], default='distance', max_length=16),
        ),
    ]
