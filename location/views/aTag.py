
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
from location.models.Tag import Tag


class aSuggestTags(aHelper, FilterClass, ListView):
  model = Tag

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    ''' Get suggestions based on query '''
    query = self.request.GET.get('query', False)
    suggestions = Tag.objects.filter(name__icontains=strip_tags(query)) | Tag.objects.filter(parent__name__icontains=strip_tags(query))
    ''' Remove already active tags if location is set '''
    if location:
      suggestions = suggestions.exclude(locations=location)
    suggestions = suggestions.exclude(children__gt=0).order_by('name').distinct()
    suggestions = self.filter(suggestions)
    response = []
    for suggestion in suggestions:
      response.append(
        f"{ suggestion.parent.name }: { suggestion.name }" if suggestion.parent else suggestion.name,
      )
    return JsonResponse(response, safe=False)

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
    response['data']['values'] = []
    ''' Filter tags by status and visibility '''
    tags = self.filter(tags).order_by('parent__name', 'name').distinct()
    ''' Add tags to response '''
    for tag in tags:
      response['data']['values'].append({
        'id': tag.id,
        'slug': tag.slug,
        'parent': f"{ tag.parent.name }" if tag.parent else '',
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
      parent = Tag.objects.get_or_create(name__iexact=parent, defaults={'name': parent, 'slug': slugify(parent), 'user':self.request.user, 'status':'p', 'visibility':'c'})[0]
    tag = Tag.objects.get_or_create(name__iexact=query, defaults={'name': query, 'slug': slugify(query), 'user':self.request.user, 'status':'p', 'visibility':'c', 'parent': parent})
    ''' Store if tag is created or used '''
    response['data']['message'] = _('Tag created and applied') if tag[1] else _('Tag applied')
    ''' Add tag to response '''
    tag = tag[0]
    response['data']['tag'] = {
      'id': tag.id,
      'name': tag.name,
      'url': tag.get_absolute_url(),
      'locations': tag.locations.count(),
    }
    ''' Add tag to location if not already present, remove if present '''
    if tag in location.tags.all():
      location.tags.remove(tag)
      response['data']['status'] = f"{ tag.name } { _('removed from location') }"
    else:
      location.tags.add(tag)
      response['data']['status'] = f"{ tag.name } { _('added to location') }"
    return JsonResponse(response)