
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
    response['data']['values'] = []
    ''' Filter tags by status and visibility '''
    chains = chains.order_by('name').distinct()
    ''' Add tags to response '''
    for chain in chains:
      response['data']['values'].append({
        'id': chain.id,
        'parent': f"{ chain.parent.name }" if chain.parent else '',
        'name': chain.name,
        'url': chain.get_absolute_url(),
        'locations': chain.locations.count(),
      })
    return JsonResponse(response)
  
class aAddChain(aHelper, UpdateView):
  model = Location
  fields = ['chain']

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Validate Chain '''
    query = self.request.GET.get('value', False)
    ''' Remove HTML tags from tags and remove whitespace '''
    query = strip_tags(query).strip()
    parent = None
    if ':' in query:
      parent = query.split(':')[0].strip()
      query = query.split(':')[-1].strip()
    response = self.getDefaultData()
    if not query or len(query) <  3:
      return self.getInputError('tag', 'No tag provided or tag too short')
    ''' Select tag or create tag based on query input '''
    if parent:
      parent = Chain.objects.get_or_create(name__iexact=parent, defaults={'name': parent, 'slug': slugify(parent), 'user':self.request.user})[0]
    chain = Chain.objects.get_or_create(name__iexact=query, defaults={'name': query, 'slug': slugify(query), 'user':self.request.user, 'parent': parent})
    ''' Store if chain is created or used '''
    response['data']['message'] = _('Chain created and applied') if chain[1] else _('Chain applied')
    ''' Add chain to response '''
    chain = chain[0]
    response['data']['value'] = {
      'id': chain.id,
      'name': chain.name,
      'url': chain.get_absolute_url(),
      'locations': chain.locations.count(),
    }
    ''' Add tag to location if not already present, remove if present '''
    if chain in location.chain.all():
      location.chain.remove(chain)
      response['data']['status'] = f"{ chain.name } { _('removed from location') }"
    else:
      location.chain.add(chain)
      response['data']['status'] = f"{ chain.name } { _('added to location') }"
    return JsonResponse(response)