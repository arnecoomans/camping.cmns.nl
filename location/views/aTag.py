
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

from location.models.Location import Location
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

class aAddTag(aHelper, UpdateView):
  model = Location
  
  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Validate Tag '''
    tag = self.request.POST.get('tag', False) or self.request.GET.get('tag', False)
    try:
      tag = int(tag) if tag else False
    except:
      tag = False
    if not tag:
      return self.getInputError('tag', 'No tag provided or tag is invalid.')
    ''' Proceed processing request '''
    response = self.getDefaultData()
    ''' Togggle Tag '''
    if tag in location.tags.all().values_list('id', flat=True):
      ''' Remove Tag '''
      location.tags.remove(tag)
      response['data']['tag'] = {
        'name': tag,
        'action': 'removed',
      }
    else:
      ''' Add Tag '''
      location.tags.add(tag)
      response['data']['tag'] = {
        'name': tag,
        'action': 'added',
        'tags': list(location.tags.all().values_list('id', flat=True)),
      }
    return JsonResponse(response)