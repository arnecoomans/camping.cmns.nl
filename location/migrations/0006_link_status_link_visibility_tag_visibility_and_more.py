# Generated by Django 4.2.6 on 2023-10-22 19:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0005_listlocation_status_listlocation_visibility_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='status',
            field=models.CharField(choices=[('p', 'published'), ('r', 'revoked'), ('x', 'deleted')], default='p', max_length=1),
        ),
        migrations.AddField(
            model_name='link',
            name='visibility',
            field=models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1),
        ),
        migrations.AddField(
            model_name='tag',
            name='visibility',
            field=models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1),
        ),
        migrations.AlterField(
            model_name='location',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='visibility',
            field=models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1),
        ),
    ]
