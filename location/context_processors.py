from django.conf import settings

# Define content that will be available in templates
def setting_data(request):
  return {
    'app_title': settings.APP_TITLE,
    'meta_description': settings.META_DESCRIPTION,
    'language_code': settings.LANGUAGE_CODE,
    'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    'default_order': settings.DEFAULT_ORDER,
    'allow_unauthenticated_read_comments': settings.ALLOW_UNAUTHENTICATED_READ_COMMENTS,
  }
