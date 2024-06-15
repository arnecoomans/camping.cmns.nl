
from django.views.generic.list import ListView
from django.views.generic.edit import  UpdateView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.text import slugify

from .snippets.a_helper import aHelper
from .snippets.filter_class import FilterClass

from location.models.Location import Location
from location.models.Location import Chain

class aSuggestChain(aHelper, FilterClass, ListView):
  model = Chain

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    ''' Get suggestions based on query '''
    query = self.request.GET.get('query', False)
    if not query or len(query) == 0:
      suggestions = Chain.objects.all()
    else:
      suggestions = Chain.objects.filter(name__icontains=strip_tags(query)) | Chain.objects.filter(parent__name__icontains=strip_tags(query))
    ''' Remove already active tags if location is set '''
    if location:
      suggestions = suggestions.exclude(locations=location)
    suggestions = suggestions.exclude(children__gt=0).order_by('name').distinct()
    response = []
    for suggestion in suggestions:
      response.append(
        f"{ suggestion.parent.name }: { suggestion.name }" if suggestion.parent else suggestion.name,
      )
    return JsonResponse(response, safe=False)

class aListChains(aHelper, FilterClass, ListView):
  model = Chain

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Proceed processing request '''
    response = self.getDefaultData()
    chains = Chain.objects.all()
    ''' Process Filters '''
    if location:
      chains = chains.filter(locations=location)
    response['data']['chains'] = []
    ''' Filter tags by status and visibility '''
    chains = chains.order_by('name').distinct()
    ''' Add tags to response '''
    for chain in chains:
      response['data']['chains'].append({
        'id': chain.id,
        'parent': f"{ chain.parent.name }: " if chain.parent else '',
        'name': chain.name,
        'url': chain.get_absolute_url(),
        'locations': chain.locations.count(),
      })
    return JsonResponse(response)