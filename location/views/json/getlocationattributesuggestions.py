from django.views.generic import View, TemplateView, DetailView, ListView
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.template.loader import render_to_string

from ..snippets.filter_class import FilterClass

from location.models.Location import Location, Category, Chain
from location.models.Tag import Tag
from location.models.Comment import Comment

''' JSONGetLocationAttributeSuggestions
    This view is used to suggest attributes of a location
    Attributes are: categories, chains, tags
    The view will return a JsonResponse with the requested attributes

'''
class JSONGetLocationAttributeSuggestions(View, FilterClass):
  def __init__(self, *args, **kwargs):
    super().__init__(**kwargs)
    self.mapping = {
      'category': {
        'model': Category,
      },
      'chain': {
        'model': Chain,
      },
      'tag': {
        'model': Tag,
      },
    }
    self.model = None
    self.location = None
    self.query = None

  ''' get_model 
      This method will return the model based on the model mentioned
      in the kwargs.
      /json/getSuggestions/<model>/<location>/    
  '''
  def get_model(self):
    if self.model == None:
      model = self.kwargs['model'].lower().strip()
      if model in self.mapping:
        self.model = self.mapping[model]['model']
      else:
        raise Exception(f"model { model } not supported")
    return self.model
  
  def get_location(self):
    if self.location == None:
      location = self.kwargs['location'].lower().strip()
      try:
        self.location = Location.objects.get(slug=location)
      except Location.DoesNotExist:
        self.location = False
      except Exception as e:
        raise Exception(f"location { location } raised an error: { e }")
        # Location is not required, so do not throw an exception
        # raise Exception(f"Location { location } not found")
    return self.location
  
  def get_query(self):
    if self.query == None:
      if 'query' in self.request.GET:
        self.query = self.request.GET.get('query', None)
      elif 'query' in self.request.POST:
        self.query = self.request.POST.get('query', None)
      elif 'query' in self.kwargs:
        self.query = self.kwargs['query']
      else:
        self.query = False
      self.query = self.query.lower().strip() if self.query else False
    return self.query

  def get_queryset(self):
    model = self.get_model()
    queryset = model.objects.all()
    ''' If location is set, filter queryset by location'''
    location = self.get_location()
    if location:
      if 'locations' in [field.name for field in model._meta.get_fields()]:
        queryset = queryset.exclude(locations=location)
      elif 'location' in [field.name for field in model._meta.get_fields()]:
        queryset = queryset.exclude(location=location)
      if 'secondary_for' in [field.name for field in model._meta.get_fields()]:
        queryset = queryset | queryset.exclude(secondary_for=location)
      if 'children' in [field.name for field in model._meta.get_fields()]:
        queryset =  queryset.exclude(children__gt=0)
    ''' If query is set, filter queryset by query '''
    query = self.get_query()
    if query:
      queryset = queryset.filter(name__icontains=query)
    ''' Filter queryset '''
    queryset = self.filter(queryset)
    queryset = queryset.order_by('name')
    return queryset

  def get(self, request, *args, **kwargs):
    # queryset = self.get_queryset()
    try:
      queryset = self.get_queryset()
    except Exception as e:
      return JsonResponse({'message': f"{ _('error when fetching queryset') }: { e }"}, status=500)
    if queryset.count() == 0:
      return JsonResponse({'message': f"{ _('no suggestions found') }"}, status=200)
    ''' Build Response '''
    payload = []
    for suggestion in queryset:
      parent = f"{ suggestion.parent.name }: " if suggestion.parent else ''
      text = f"{ parent }{ suggestion.name }"
      # import re
      # rendered_text = re.sub(f"({ self.get_query() })", r"<strong>\1</strong>", text, flags=re.IGNORECASE)
      payload.append({ 'text': text, 'slug': suggestion.slug })
    return JsonResponse({'payload': payload}, status=200)
