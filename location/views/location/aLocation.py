
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
    return JsonResponse(suggestions, safe=False)
