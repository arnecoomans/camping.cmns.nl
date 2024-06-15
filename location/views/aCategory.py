
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
from location.models.Location import Category


class aSuggestCategories(aHelper, FilterClass, ListView):
  model = Category

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    ''' Get suggestions based on query '''
    query = self.request.GET.get('query', False)
    if not query or len(query) == 0:
      suggestions = Category.objects.all()
    else:
      suggestions = Category.objects.filter(name__icontains=strip_tags(query)) | Category.objects.filter(parent__name__icontains=strip_tags(query))
    ''' Remove already active Categories if location is set '''
    if location:
      suggestions = suggestions.exclude(locations=location).exclude(secondary_for=location)
    suggestions = suggestions.exclude(children__gt=0).order_by('parent__name', 'name').distinct()
    response = []
    for suggestion in suggestions:
      response.append(
        f"{ suggestion.parent.name }: { suggestion.name }" if suggestion.parent else suggestion.name,
      )
    return JsonResponse(response, safe=False)

class aListCategories(aHelper, FilterClass, ListView):
  model = Category

  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Proceed processing request '''
    response = self.getDefaultData()
    category = location.category
    additional_categories = location.additional_category
    response['data']['values'] = []
    for category in additional_categories.all():
      response['data']['values'].append(
        {
          'id': category.id,
          'name': category.name,
          'url': category.get_absolute_url(),
          'locations': category.locations.count(),
          'parent': f"{ category.parent.name }"if category.parent else '',
          'primary': 0,
        }
      )
    return JsonResponse(response)

class aAddCategory(aHelper, UpdateView):
  model = Location
  
  def get(self, request, *args, **kwargs):
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Validate Category '''
    query = self.request.GET.get('value', False)
    ''' Remove HTML Categorys from Categorys and remove whitespace '''
    query = strip_tags(query).strip()
    parent = False
    if ':' in query:
      parent = query.split(':')[0].strip()
      query = query.split(':')[-1].strip()
    response = self.getDefaultData()
    if not query or len(query) <  3:
      return self.getInputError('Category', 'No Category provided or Category too short')
    ''' Select Category or create Category based on query input '''
    if parent:
      parent = Category.objects.get_or_create(name__iexact=parent, defaults={'name': parent, 'slug': slugify(parent), 'user':self.request.user, 'status':'p', 'visibility':'c'})[0]
    category = Category.objects.get_or_create(name__iexact=query, defaults={'name': query, 'slug': slugify(query), 'user':self.request.user, 'status':'p', 'visibility':'c', 'parent': parent})
    ''' Store if Category is created or used '''
    response['data']['message'] = _('Category created and applied') if category[1] else _('Category applied')
    ''' Add Category to response '''
    category = category[0]
    response['data']['value'] = {
      'id': category.id,
      'name': category.name,
      'url': category.get_absolute_url(),
      'locations': category.locations.count(),
    }
    ''' Add Category to location if not already present, remove if present '''
    
    if location.category == category:
      ''' Main location category cannot be changed in this interface, avoid duplicates '''
      response['data']['status'] = f"{ category.name } { _('is already the main category') }"
    elif category in location.additional_category.all():
      location.additional_category.remove(category)
      response['data']['status'] = f"{ category.name } { _('removed from location') }"
    else:
      location.additional_category.add(category)
      response['data']['status'] = f"{ category.name } { _('added to location') }"
    return JsonResponse(response)