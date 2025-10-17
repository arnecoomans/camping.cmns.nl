from django.views.generic import View, TemplateView, DetailView, ListView
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.template.loader import render_to_string
from types import NoneType
from django.db.models.fields.related import ForeignKey, ManyToManyField

from ..snippets.filter_class import FilterClass
from location.models.Location import Location, Category, Chain, Size
from location.models.Tag import Tag
from location.models.Comment import Comment

''' JSONGetLocationAttributes 
    This view is used to get all attributes of a location
    Attributes are: categories, chains, tags, comments
    The view will return a JsonResponse with the requested attributes

'''
class JSONGetLocationAttributes(View, FilterClass):

  def get_attribute(self):
    supported_attributes = ['category', 'chain', 'tag', 'comment', 'actionlist', 
                            'maps_permission', 'show_category_label', 'filter_by_distance', 'hide_least_liked',
                            'link', 'size']
    translated_attributes = {
      'favorite': 'actionlist',
      'dislike': 'actionlist',
    }
    attribute = self.kwargs['attribute'].lower().strip()
    if attribute in supported_attributes:
      return attribute
    elif attribute in translated_attributes:
      return translated_attributes[attribute]
    return None
  
  def get_queryset(self, location=None):
    if self.get_attribute() == 'category':
      queryset = Category.objects.all()
    elif self.get_attribute() == 'chain':
      queryset = Chain.objects.all()
    elif self.get_attribute() == 'tag':
      queryset = Tag.objects.all()
    elif self.get_attribute() == 'comment':
      queryset = Comment.objects.all()
    elif self.get_attribute() == 'actionlist':
      return Location.objects.filter(slug=location.slug)
    elif self.get_attribute() == 'link':
      return location.link.all()
    elif self.get_attribute() == 'size':
      return location.size
    elif self.get_attribute() in ['maps_permission', 'show_category_label', 'filter_by_distance', 'hide_least_liked']:
      ''' Profile Boolean Fields '''
      return getattr(self.request.user.profile, self.get_attribute())
    else:
      raise Exception(f"Queryset for attribute { self.get_attribute() } not supported")
    model = queryset.model
    if location:
      if self.get_attribute() == 'category':
        queryset = queryset.filter(locations=location) | queryset.filter(secondary_for=location)
      elif 'locations' in [field.name for field in model._meta.get_fields()]:
        queryset = queryset.filter(locations=location)
      elif 'location' in [field.name for field in model._meta.get_fields()]:
        queryset = queryset.filter(location=location)
      else:
        raise Exception(f"Queryset for attribute { self.get_attribute() } not supported")
    if 'name' in [field.name for field in model._meta.get_fields()]:
      queryset = queryset.order_by('name')
    else:
      queryset = queryset.order_by('date_added')
    queryset = self.filter(queryset)
    queryset = queryset.distinct()
    return queryset

  def get(self, request, *args, **kwargs):
    ''' Fetch location '''
    if kwargs['location'] == 'profile':
      location = request.user.profile
    else:
      try:
        location = Location.objects.get(slug=kwargs['location'])
      except Location.DoesNotExist:
        return JsonResponse({'message': f"{ _('location not found').capitalize() }: { kwargs['location'] }"}, status=404)
    ''' Fetch attribute to process '''
    attribute = self.get_attribute()
    if not attribute:
      return JsonResponse({'message': f"{ _('attribute not supported').capitalize() }: { self.kwargs['attribute'].lower().strip() }"}, status=400)
    ''' Build Queryset'''
    try:
      queryset = self.get_queryset(location=location)
    except Exception as e:
      return JsonResponse({'message': f"{ _('queryset not supported').capitalize() }: { e }"}, status=500)
    ''' Process Additional Field'''
    field = self.request.GET.get('field', None)
    if field:
      field_data = self.filter(getattr(location, field).all())
    # if not queryset:
    #   return JsonResponse({'message': f"{ _('No {} data found for location').format(attribute) } { location }"}, status=500)
    ''' Build Response '''
    response = []
    if type(queryset) == bool:
      response.append(render_to_string(f'partial/{ attribute }.html', {attribute: queryset, 'location': location, 'user': request.user}, request=request))
    elif type(queryset) == NoneType:
      response.append(render_to_string(f'partial/{ attribute }.html', {attribute: None, 'location': location, 'user': request.user}, request=request))
    elif type(queryset) in (Size, ):
      response.append(render_to_string(f'partial/{ attribute }.html', {attribute: queryset, 'location': location, 'user': request.user}, request=request))
    else:  
      for object in queryset:
        seperator = '' if queryset.last() == object else ', '
        if field:
          payload = render_to_string(f'partial/{ attribute }.html', {attribute: object, 'location': location, 'user': request.user, field:field_data}, request=request)
        else:
          payload = render_to_string(f'partial/{ attribute }.html', {attribute: object, 'location': location, 'user': request.user}, request=request)
        response.append(payload + seperator)
    return JsonResponse({'payload': response,}, status=200)