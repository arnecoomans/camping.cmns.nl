from django.views.generic.list import ListView
from django.views.generic.edit import  UpdateView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.text import slugify

from .snippets.a_helper import aHelper
from .snippets.filter_class import FilterClass

from location.models.Profile import Profile


class aToggleFavorite(aHelper, UpdateView):
  model = Profile

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Validate that user is logged in '''
    if self.verifyUserAuthenticated() is not True:
      return self.verifyUserAuthenticated()
    ''' Proceed processing request '''
    response = self.getDefaultData()
    ''' Verify that the user has a profile. If not, create a profile '''
    if hasattr(self.request.user, 'profile'):
      profile = self.request.user.profile
    else:
      profile = Profile.objects.create(user=self.request.user)
      #messages.add_message(self.request, messages.INFO, f"Created profile for { self.request.user.get_full_name() }")
    if location in profile.favorite.all():
      self.request.user.profile.favorite.remove(location)
      response['data']['favorite'] = False
      response['data']['message'] = _('Location removed from your likes.')
    else:
      self.request.user.profile.favorite.add(location)
      response['data']['favorite'] = True
      response['data']['message'] = _('Location added to your likes.')
    return JsonResponse(response)