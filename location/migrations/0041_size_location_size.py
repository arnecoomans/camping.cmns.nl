# Generated by Django 5.1 on 2024-12-28 09:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0040_rename_title_link_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1)),
                ('status', models.CharField(choices=[('p', 'published'), ('r', 'revoked'), ('x', 'deleted')], default='p', max_length=1)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='Name of size', max_length=255)),
                ('display_name', models.CharField(help_text='Name of size as displayed', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Markdown is supported')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='location',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='locations', to='location.size'),
        ),
    ]