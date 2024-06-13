
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import strip_tags

from .snippets.a_helper import aHelper
from .snippets.filter_class import FilterClass

from location.models.Tag import Tag


class aListTags(aHelper, FilterClass, ListView):
  model = Tag

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Proceed processing request '''
    response = self.getDefaultData()
    tags = Tag.objects.all()
    ''' Process Filters '''
    if location:
      tags = tags.filter(locations=location)
    response['data']['tags'] = []
    ''' Filter tags by status and visibility '''
    tags = self.filter(tags).order_by('name').distinct()
    ''' Add tags to response '''
    for tag in tags:
      response['data']['tags'].append({
        'id': tag.id,
        'name': tag.name,
        'url': tag.get_absolute_url(),
        'locations': tag.locations.count(),
      })
    return JsonResponse(response)
