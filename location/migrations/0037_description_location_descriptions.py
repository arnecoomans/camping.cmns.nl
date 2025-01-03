# Generated by Django 5.1 on 2024-10-15 12:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0036_alter_region_order'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('p', 'public'), ('c', 'commmunity'), ('f', 'family'), ('q', 'private')], default='c', max_length=1)),
                ('status', models.CharField(choices=[('p', 'published'), ('r', 'revoked'), ('x', 'deleted')], default='p', max_length=1)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(blank=True, help_text='Markdown is supported')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='location',
            name='descriptions',
            field=models.ManyToManyField(blank=True, related_name='locations', to='location.description'),
        ),
    ]
