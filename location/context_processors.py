from django.conf import settings

# Define content that will be available in templates
def setting_data(request):
  return {
    'app_title': settings.APP_TITLE if hasattr(settings, 'APP_TITLE') else 'VKNT',
    'meta_description': settings.META_DESCRIPTION if hasattr(settings, 'META_DESCRIPTION') else 'Online vacation planning tool',
    'language_code': settings.LANGUAGE_CODE,
    'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    'default_order': settings.DEFAULT_ORDER if hasattr(settings, 'DEFAULT_ORDER') else 'distance',
    'allow_unauthenticated_read_comments': settings.ALLOW_UNAUTHENTICATED_READ_COMMENTS if hasattr(settings, 'ALLOW_UNAUTHENTICATED_READ_COMMENTS') else False,
    'allow_unauthenticated_see_overview_map': settings.ALLOW_UNAUTHENTICATED_SEE_OVERVIEW_MAP if hasattr(settings, 'ALLOW_UNAUTHENTICATED_SEE_OVERVIEW_MAP') else False,
    'departure_center': settings.DEPARTURE_CENTER if hasattr(settings, 'DEPARTURE_CENTER') else 'Domplein, Utrecht',
  }
