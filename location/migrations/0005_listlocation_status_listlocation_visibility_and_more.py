# Generated by Django 4.2.6 on 2023-10-22 19:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0004_alter_comment_date_added_alter_comment_date_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='listlocation',
            name='status',
            field=models.CharField(choices=[('p', 'published'), ('r', 'revoked'), ('x', 'deleted')], default='p', max_length=1),
        ),
        migrations.AddField(
            model_name='listlocation',
            name='visibility',
            field=models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1),
        ),
        migrations.AlterField(
            model_name='list',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='list',
            name='visibility',
            field=models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1),
        ),
        migrations.AlterField(
            model_name='listlocation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]