from django.views.generic import View, TemplateView, DetailView, ListView
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.template.loader import render_to_string

from ..snippets.filter_class import FilterClass
from location.models.Location import Location, Category, Chain, Size
from location.models.Tag import Tag
from location.models.Comment import Comment

''' JSONGetLocationAttributes 
    This view is used to get all attributes of a location
    Attributes are: categories, chains, tags, comments
    The view will return a JsonResponse with the requested attributes

'''
class JSONGetLocationSuggestions(FilterClass, View):

  def get_location_query(self):
    query = None
    if 'query' in self.kwargs:
      query = self.kwargs['query']
    elif 'query' in self.request.GET:
      query = self.request.GET['query']
    elif 'query' in self.request.POST:
      query = self.request.POST['query']
    if len(query) > 1:
      return query
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

class JSONGetAttributeOptions(View):
  def get(self, request, *args, **kwargs):
    payload = []
    ''' Get Location '''
    location = None
    if self.kwargs['location']:
      try:
        location = Location.objects.get(slug=self.kwargs['location'])
      except:
        pass
    ''' Get Model '''
    model = self.kwargs['model'].strip().lower()
    ''' Get Model Values '''
    if model == 'size':
      queryset = Size.objects.all()
    if queryset: 
      for object in queryset:
        payload.append(render_to_string('partial/option' + model + '.html', {'object': object, 'location': location}))
    ''' Return values'''
    return JsonResponse({'payload': payload})
    