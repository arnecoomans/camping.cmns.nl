from django.views.generic import View, TemplateView, DetailView, ListView
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.template.loader import render_to_string

from ..snippets.filter_class import FilterClass
from location.models.Location import Location, Category, Chain
from location.models.Tag import Tag
from location.models.Comment import Comment

''' JSONGetLocationAttributes 
    This view is used to get all attributes of a location
    Attributes are: categories, chains, tags, comments
    The view will return a JsonResponse with the requested attributes

'''
class JSONGetLocationSuggestions(FilterClass, View):

  def get_location_query(self):
    if 'query' in self.kwargs:
      return self.kwargs['query']
    elif 'query' in self.request.GET:
      return self.request.GET['query']
    elif 'query' in self.request.POST:
      return self.request.POST['query']
    else:
      return None
    
  def get(self, request, *args, **kwargs):
    if self.get_location_query() is None:
      return JsonResponse([], safe=False)
    queryset = Location.objects.filter(name__icontains=self.get_location_query())
    queryset = self.filter(queryset)
    payload = []
    for location in queryset: 
      payload.append({
        'slug': location.slug,
        'name': location.name,
        'url': location.get_absolute_url(),
        'country': location.country().name,
      })
    return JsonResponse({'payload': payload})