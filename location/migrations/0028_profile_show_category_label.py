# Generated by Django 5.1 on 2024-08-24 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0027_listlocation_show_on_route'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='show_category_label',
            field=models.BooleanField(default=True, help_text='Show category label on location list page'),
        ),
    ]
