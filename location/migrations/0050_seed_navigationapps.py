from django.db import migrations

def create_navigation_apps(apps, schema_editor):
  """
  Create or update default NavigationApps rows.
  This is idempotent: safe to run multiple times.
  """
  NavigationApps = apps.get_model('location', 'NavigationApps')
  defaults = [
    {
      'slug': 'google-maps',
      'name': 'Google Maps',
      'url_format': 'https://www.google.com/maps/dir//{address}',
      'default_enabled': True,
    },
    {
      'slug': 'waze',
      'name': 'Waze',
      'url_format': 'https://waze.com/ul?q={address}',
      'default_enabled': True,
    },
    {
      'slug': 'apple-maps',
      'name': 'Apple Maps',
      'url_format': 'https://maps.apple.com/search?query={address}',
      'default_enabled': False,
    },
  ]
  for data in defaults:
    NavigationApps.objects.update_or_create(
      slug=data['slug'],
      defaults=data,
    )

class Migration(migrations.Migration):

    dependencies = [
        ('location', '0049_navigationapps_default_enabled'),
    ]

    operations = [
       migrations.RunPython(create_navigation_apps, migrations.RunPython.noop),
    ]
