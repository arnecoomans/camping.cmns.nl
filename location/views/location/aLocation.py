
from django.views.generic.list import ListView
from django.views.generic.edit import  UpdateView
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.utils.text import slugify

from ..snippets.a_helper import aHelper
from ..snippets.filter_class import FilterClass

from location.models.Location import Location, Category, Chain, Region
from location.models.Tag import Tag


class aSuggestLocations(aHelper, FilterClass, ListView):
  model = Location

  ''' Suggest Locations, Categories, Regions, Chains and Tags 
      based on query string.
      Do not return the matching location, category, region, chain or tag, but auto-complete 
      the queried word.
      The code:
        for word in query.name.split():
      takes the search result, matches the searched word in the search result and
      only adds the complete word as search suggestion. This maintains the functionality
      of search suggestions and does not make the search suggestions list a search result list.
  '''
      
  def get(self, request, *args, **kwargs):
    ''' Fetch query from URL ?query= parameter '''
    query = self.request.GET.get('q', False)
    if query:
      ''' Build Suggestion List '''
      suggestions = []
      ''' Suggest locations '''
      locations = Location.objects.filter(name__icontains=query)
      for location in locations:
        for word in location.name.split():
          if query.lower() in word.lower():
            if word not in suggestions:
              suggestions.append(word)
      ''' Suggest categories '''
      categories = Category.objects.filter(name__icontains=query)
      for category in categories:
        for word in category.name.split():
          if query.lower() in word.lower():
            if word not in suggestions:
              suggestions.append(word)
      ''' Suggest Regions '''
      regions = Region.objects.filter(name__icontains=query) | Region.objects.filter(parent__name__icontains=query) | Region.objects.filter(parent__parent__name__icontains=query)
      for region in regions:
        for word in region.name.split():
          if query.lower() in word.lower():
            if word not in suggestions:
              suggestions.append(word)
      ''' Suggest chains '''
      chains = Chain.objects.filter(name__icontains=query) | Chain.objects.filter(parent__name__icontains=query)
      for chain in chains:
        for word in chain.name.split():
          if query.lower() in word.lower():
            if word not in suggestions:
              suggestions.append(word)
      ''' Suggest tags '''
      tags = Tag.objects.filter(name__icontains=query) |  Tag.objects.filter(parent__name__icontains=query)
      for tag in tags:  
        if tag.name not in suggestions:
          suggestions.append(tag.name)
    ''' Case insensitive suggestions '''
    lower_suggestions = []
    for suggestion in suggestions:
      ''' If suggestion is already in caps-insensitive list, remove it '''
      if suggestion.lower() in lower_suggestions:
        suggestions.remove(suggestion)
      else:
        ''' If suggestion is not in caps-insensitive list, add it '''
        if suggestion != suggestion.capitalize():
          ''' If suggestion is not capitalized, add capitalized version'''
          suggestions.remove(suggestion)
          suggestions.append(suggestion.capitalize())
        ''' Add lowercase version to list '''
        lower_suggestions.append(suggestion.lower())
    ''' Return suggestions '''  
    return JsonResponse(suggestions, safe=False)
