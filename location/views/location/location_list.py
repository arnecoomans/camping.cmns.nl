from django.views.generic.list import ListView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.db.models import Avg
from django.shortcuts import redirect
from django.utils.html import escape

from ..snippets.filter_class import FilterClass

from math import floor, ceil

from location.models.Location import Location, Size

''' MASTER VIEWS '''
''' Location List Master View
    The Master View holds the logic used in both the search (all), location and activity view. It:
    - adds active filters to the context data
    - adds function filter_queryset, that returns the queryset based on the active filters
'''
class LocationListMaster(FilterClass):
  template_name = 'location/location/location_list.html'

  def get_default_order(self):
    if hasattr(self.request.user, 'profile'):
      return self.request.user.profile.order
    return settings.DEFAULT_ORDER

  ''' Get Active Filters 
      Process URL and Parameters to build a list of active filters. This is used in the context to
      fill active_filters, and used in the search query to process the active filters.
  '''
  def get_active_filters(self, query=None):
    ''' Use cached version if available (on 2nd or later request) '''
    if hasattr(self, 'active_filters'):
      if query == None:
        return self.active_filters
      return self.active_filters[query] if query in self.active_filters else None
    else:
      self.active_filters = {}
      ''' Fetch Active Filters '''
      ''' Kwargs filters 
          are part of the url structure and defined in urls.py
      '''
      for field in ['country', 'region', 'department', ]:
        if field in self.kwargs:
          self.active_filters[field] = self.kwargs[field]
      ''' Query filters
          are part of the request but not part of the url
      '''
      for field in ['category', 'tag', 'chains', 'q', 'only', 'size', ]:
        if self.request.GET.get(field, False):
          ''' All values in query parameters should be a list.
              Multiple values are seperated by a , resulting in multiple list items
          '''
          value = self.request.GET.get(field, '').split(',')
          ''' Strip whitespaces for all items in list'''
          value = [word.strip() for word in value]
          self.active_filters[field] = value
      ''' Boolean filters 
          If query is mentioned in query without value, it should be set as True
          If the query has a value, the value should be set
          If the value is "false", the value should be False
      '''
      for field in ['favorites', 'visited', ]:
        if field in self.request.GET and self.request.GET.get(field, '').lower() != 'false':
          if self.request.GET.get(field, '') == '':
            self.active_filters[field] = True
          else:
            self.active_filters[field] = self.request.GET.get(field, '')
    ''' Special filters  are only set if they are not the default value '''
    self.active_filters['order'] = self.request.GET.get('order', self.get_default_order())
    if not self.request.GET.get('min', None) == None:
      self.active_filters['dist_min'] = self.request.GET.get('min', None)
    if not self.request.GET.get('max', None) == None:
      self.active_filters['dist_max'] = self.request.GET.get('max', None)
    if self.get_active_visibility():
      self.active_filters['visibility'] = self.get_active_visibility()
    ''' Return value ''' 
    if query:
      return self.active_filters[query] if query in self.active_filters else None
    return self.active_filters

  def get_available_filters(self, query=None):
    if hasattr(self, 'available_filters'):
      if query:
        return self.available_filters[query] if query in self.available_filters else None
      return self.get_available_filters
    else:
      self.available_filters = {}
      ''' Available Country Filters '''
      self.available_filters['countries']     = self.get_queryset().values('location__parent__parent__slug', 'location__parent__parent__name').order_by('location__parent__parent__order').distinct()
      self.available_filters['regions']       = self.get_queryset().values('location__parent__slug', 'location__parent__name').order_by().distinct()
      self.available_filters['departments']   = self.get_queryset().values('location__slug', 'location__name').order_by().distinct()
      ''' Available Tag Filters '''
      self.available_filters['tags']          = self.get_queryset().values('tags__slug', 'tags__name', 'tags__parent__name').exclude(tags__name=None).exclude(tags__hide_from_filterlist=True).order_by('tags__parent__name', 'tags__name').distinct()
      self.available_filters['categories']    = self.get_queryset().values('category__slug', 'category__name').order_by().distinct()
      ''' Special Filters '''
      if hasattr(self.request.user, 'profile'):
        self.available_filters['has_favorites'] = True if self.get_queryset().filter(favorite_of=self.request.user.profile).count() > 1 else False
        self.available_filters['has_visited']   = True if self.get_queryset().filter(visitors__user=self.request.user).count() > 1 else False
      self.available_filters['order']           = ['distance', 'region']
      self.available_filters['size']            = self.get_available_sizes()
      self.available_filters['visibility']      = self.get_available_visibilities()
      self.available_filters['chains']           = self.get_available_chains()
      return self.available_filters
  

  ''' Active Visibility 
      Returns a list of the active visibility as well as its display value
  '''
  def get_active_visibility(self):
    visibility = None
    if self.request.GET.get('visibility', False):
      display = None
      for key, value in Location.visibility_choices:
        if key == self.request.GET.get('visibility', False):
          display = value
      visibility = (self.request.GET.get('visibility', False), display)
    return visibility
  ''' Available Visibilities 
      Returns a list of available visibilities based on the visibilities used in the queryset
  '''
  def get_available_visibilities(self):
    available_visibilities = Location.visibility_choices
    used_visibilities = self.get_queryset().values_list('visibility', flat=True).order_by().distinct()
    available_visibilities = [visibility for visibility in available_visibilities if visibility[0] in used_visibilities]
    return available_visibilities
  ''' Range '''
  def get_range(self):
    location_list = self.get_queryset().exclude(category__name__iexact='home').exclude(distance_to_departure_center=None).order_by('distance_to_departure_center')
    try:
      min = location_list.first().distance_to_departure_center
      max = location_list.last().distance_to_departure_center
    except AttributeError:
      min = 0
      max = 0
    min = floor(min/100)*100
    max = ceil(max/100)*100
    count_steps = ceil(max/100) - floor(min/100)
    steps = [min]
    i = 1
    while i < count_steps:
      steps.append(min + i*100)
      i += 1
    steps.append(max)
    return {
      'min': min,
      'max': max,
      'steps': steps
    }

  def get_available_chains(self):
    return self.get_queryset().filter(chains__children=None).exclude(chains__name=None).values('chains__slug', 'chains__name').order_by().distinct()
  
  def get_available_sizes(self):
    return self.get_queryset().exclude(size__slug__isnull=True).values('size__slug', 'size__name').order_by('size__id').distinct()
  
  ''' Filter Queryset 
      Uses get_active_filters to determine filters that need to be processed
  '''
  def filter_queryset(self, queryset):
    ''' Apply straight forward filters 
        Map filters to search query or maximum of 2 search queries
    '''
    mapping = {
      'country': 'location__parent__parent__slug__iexact',
      'region': 'location__parent__slug__iexact',
      'department': 'location__slug__iexact',
      'category': ['category__slug__in', 'additional_category__slug__in'],
      'tag': 'tags__slug__in',
      'chain': ['chain__slug__in', 'chain__parent__slug__in'],
      'visibility': 'visibility__in',
      'size': 'size__slug__in',
    }
    ''' Apply filters '''
    for field, map in mapping.items():
      if self.get_active_filters(field):
        if type(map) == str:
          queryset = queryset.filter(**{map: self.get_active_filters(field)})
        elif type(map) == list:
          queryset = queryset.filter(**{map[0]: self.get_active_filters(field)}) | queryset.filter(**{map[1]: self.get_active_filters(field)})
      ''' Apply filters that require login and a user with a profile '''
    if hasattr(self.request.user, 'profile'):
      if self.get_active_filters('favorites'):
        queryset = queryset.filter(favorite_of__user=self.request.user)
      if self.get_active_filters('visited') == True:
        queryset = queryset.filter(slug__in=self.request.user.visits.filter(status='p').values_list('location__slug', flat=True))
      elif self.get_active_filters('visited'):
        queryset = queryset.filter(slug__in=self.request.user.visits.filter(status='p', year=self.get_active_filters('visited')).values_list('location__slug', flat=True))
    ''' Free Text Search Filters '''
    if self.get_active_filters('q'):
      query = self.get_active_filters('q')
      for q in query:
        queryset = queryset.filter(name__icontains=q) |\
                   queryset.filter(address__icontains=q) |\
                   queryset.filter(owners_names__icontains=q) |\
                   queryset.filter(descriptions__description=q) |\
                   queryset.filter(category__name__icontains=q) |\
                   queryset.filter(additional_category__name__icontains=q) |\
                   queryset.filter(chains__name__icontains=q) |\
                   queryset.filter(chains__parent__name__icontains=q) |\
                   queryset.filter(tags__name__icontains=q) |\
                   queryset.filter(location__name__icontains=q) |\
                   queryset.filter(location__parent__name__icontains=q) |\
                   queryset.filter(location__parent__parent__name__icontains=q)
    ''' Min and Max Distance '''
    if self.get_active_filters('dist_min'):
      queryset = queryset.filter(distance_to_departure_center__gt=self.get_active_filters('dist_min'))
    if self.get_active_filters('dist_max'):
      queryset = queryset.filter(distance_to_departure_center__lt=self.get_active_filters('dist_max'))
    return queryset

  def order_queryset(self, queryset):
    ''' Store ordering options '''
    order = self.get_active_filters('order').lower()
    ''' Process ordering options '''
    if order == 'distance':
      queryset = queryset.annotate(
          department_average_distance=Avg("location__locations__distance_to_departure_center"),
          region_average_distance=Avg("location__parent__children__locations__distance_to_departure_center"),
          # Removed country because it added quite the processing time
          #country_average_distance=Avg("location__parent__parent__children__children__locations__distance_to_departure_center"),
      )
      queryset = queryset.order_by(
          'location__parent__parent__order', 'region_average_distance', 'department_average_distance', 'name'
      ).distinct()
    elif order == 'name':
      queryset = queryset.order_by('name')
    elif order == '-name':
      queryset = queryset.order_by('-name')
    elif order == 'date_added':
      queryset = queryset.order_by('-date_added')
    elif order == '-date_added':
      queryset = queryset.order_by('date_added')
    elif order == 'date_modified':
      queryset = queryset.order_by('-date_modified')
    elif order == 'user':
      queryset = queryset.order_by('user')
    else:
      ''' Implicit ordering by region '''
      queryset = queryset.order_by(
          'location__parent__parent__order', 'location__parent', 'location__name', 'name').distinct()
    return queryset

  ''' Get Queryset
      Get Queryset and apply required filters
  '''
  def get_queryset(self):
    if hasattr(self, 'cached_queryset'):
      return self.cached_queryset
    queryset = Location.objects.all()
    ''' Scoping '''
    if self.get_scope() == 'locations':
      queryset = queryset.exclude(category__slug=settings.ACTIVITY_SLUG).exclude(category__parent__slug=settings.ACTIVITY_SLUG)
    elif self.get_scope() == 'activities':
      queryset = queryset.filter(category__slug=settings.ACTIVITY_SLUG) | queryset.filter(category__parent__slug=settings.ACTIVITY_SLUG)
    ''' Visibility '''
    queryset = self.filter_status(queryset)
    queryset = self.filter_visibility(queryset)
    ''' Filtering '''
    queryset = self.filter_queryset(queryset)
    ''' Ordering '''
    queryset = self.order_queryset(queryset)
    self.cached_queryset = queryset
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope']            = self.get_scope()
    ''' Fetch Active Filters '''
    context['active_filters']   = self.get_active_filters()
    context['available_filters']= self.get_available_filters()
    if self.get_queryset().count() > 0:
      context['min_min_distance'] = floor(self.get_queryset().order_by('distance_to_departure_center').exclude(distance_to_departure_center=None).first().distance_to_departure_center / 100) * 100
      context['max_max_distance'] = ceil(self.get_queryset().order_by('distance_to_departure_center').exclude(distance_to_departure_center=None).last().distance_to_departure_center / 100) * 100
      context['range'] = self.get_range()
    if self.request.user.is_authenticated:
      context['visited_locations'] = self.request.user.visits.filter(status='p').values_list("location_id", flat=True)
    
    return context
  
  def get(self, request, *args, **kwargs):
    ''' Check for maps permission '''
    if self.get_queryset().count() == 1 and self.request.GET.get('q', False):
      messages.add_message(request, messages.INFO, f"{ _('Single search result found for') } { escape(self.request.GET.get('q', '')) }. { _('Redirecting to location') }.")
      return redirect(self.get_queryset().first().get_absolute_url())
    return super().get(request, *args, **kwargs)
  

class LocationListView(LocationListMaster, ListView):
  model = Location

  def get_scope(self):
    return 'locations'
  

class ActivityListView(LocationListMaster, ListView):
  model = Location

  def get_scope(self):
    return 'activities'


class AllSearchView(LocationListMaster, ListView):
  model = Location

  def get_scope(self):
    return 'all'
  
class LocationMapView(LocationListMaster, ListView):
  model = Location
  template_name = 'location/location/location_list_map.html'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['maps_permission'] = self.get_maps_permission()
    context['map_center'] = self.get_center()
    return context
  def get_scope(self):
    return 'all'
  
  ''' Get Center '''
  def get_center(self):
    lat_total = 0.0
    lng_total = 0.0
    count = 0
    for location in self.get_queryset():
      if location.coord_lat and location.coord_lng:
        lat_total += float(location.coord_lat)
        lng_total += float(location.coord_lng)
        count +=1
    return { 'lat': str(lat_total/count).replace(',','.')[:9], 'lng': str(lng_total/count).replace(',','.')[:9] }

  ''' Maps Permission
      The Location Detail Page can show a google maps view of the location. However,
      before sharing information with Google, we need to get the user's consent. 
      Consent is stored in the profile, or in a session.
  '''
  def get_maps_permission(self):
    ''' Check for ?maps_permission=true in URL '''
    if self.request.GET.get('maps_permission', False) == 'true':
      return True
    ''' Check for maps permission in profile '''
    if hasattr(self.request.user, 'profile') and self.request.user.profile.maps_permission == True:
      return True
    ''' Check for maps permission in session '''
    return True if self.request.session.get('maps_permission', False) else False