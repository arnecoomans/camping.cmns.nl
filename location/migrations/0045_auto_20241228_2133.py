# Generated by Django 5.1 on 2024-12-28 17:41

from django.db import migrations


class Migration(migrations.Migration):
    def create_clothing_sizes(apps, schema_editor):
        #User = get_user_model()
        User = apps.get_model('auth', 'User')
        user = User.objects.get(username='arnecoomans')
        if not user:
            user = User.objects.first()
            if not user:
                raise ValueError("No users found in the database. Please create a user before running this script.")

        size = apps.get_model('location', 'Size')
        sizes = [('?', 'Unsure'), ('xxs', 'Extra Extra Small (1-10)'), ('xs', 'Extra Small (10-25)'), ('s', 'Small (25-50)'), ('m', 'Medium (50-100)'), ('l', 'Large (100-150)'), ('xl', 'Extra Large (150-250)'), ('xxl', 'Extra Extra Large (250+)')]
        for sizeobj in sizes:
            size.objects.get_or_create(
                slug=sizeobj[0], 
                defaults={
                    'name': sizeobj[1], 
                    'user': user,
                    }
            )

    dependencies = [
        ('location', '0043_remove_size_display_name_size_slug_alter_size_name'),
    ]

    operations = [
        migrations.RunPython(create_clothing_sizes),
    ]
