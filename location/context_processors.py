from django.conf import settings

# Define content that will be available in templates
def setting_data(request):
  return {
    'app_title': getattr(settings, 'APP_TITLE', 'VKNT'),
    'meta_description': getattr(settings, 'META_DESCRIPTION', 'Online vacation planning tool'),#
    'language_code': getattr(settings, 'LANGUAGE_CODE', 'en'),
    'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    'default_order': getattr(settings, 'DEFAULT_ORDER', 'distance'),
    'allow_unauthenticated_read_comments': getattr(settings, 'ALLOW_UNAUTHENTICATED_READ_COMMENTS', False),
    'allow_unauthenticated_see_overview_map': getattr(settings, 'ALLOW_UNAUTHENTICATED_SEE_OVERVIEW_MAP', False),
    'departure_center': getattr(settings, 'DEPARTURE_CENTER', 'Domplein, Utrecht'),

    'ajax_load_comments': getattr(settings, 'AJAX_LOAD_COMMENTS', False),
    'ajax_load_tags': getattr(settings, 'AJAX_LOAD_TAGS', False),
    'ajax_load_categories': getattr(settings, 'AJAX_LOAD_CATEGORIES', False),
    'ajax_load_chains': getattr(settings, 'AJAX_LOAD_CHAINS', False),
    'ajax_load_actionlist': getattr(settings, 'AJAX_LOAD_ACTIONLIST', False),
    
  }