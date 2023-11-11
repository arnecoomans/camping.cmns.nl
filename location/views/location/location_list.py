from django.views.generic.list import ListView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse_lazy, reverse
from django.conf import settings

from ..snippets.filter_class import FilterClass

from location.models.Location import Location

''' MASTER VIEWS '''
''' Location List Master View
    The Master View holds the logic used in both the search (all), location and activity view. It:
    - adds active filters to the context data
    - adds function filter_queryset, that returns the queryset based on the active filters
'''
class LocationListMaster(FilterClass):

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
      for field in ['category', 'tag', 'chain', 'q', 'visibility', ]:
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
      self.available_filters['countries']     = self.get_queryset().values('location__parent__parent__slug', 'location__parent__parent__name').order_by().distinct()
      self.available_filters['regions']       = self.get_queryset().values('location__parent__slug', 'location__parent__name').order_by().distinct()
      self.available_filters['departments']   = self.get_queryset().values('location__slug', 'location__name').order_by().distinct()
      ''' Available Tag Filters '''
      self.available_filters['tags']          = self.get_queryset().values('tags__slug', 'tags__name', 'tags__parent__name').exclude(tags__name=None).order_by('tags__parent__name', 'tags__name').distinct()
      self.available_filters['categories']    = self.get_queryset().values('category__slug', 'category__name').order_by().distinct()
      ''' Special Filters '''
      if hasattr(self.request.user, 'profile'):
        self.available_filters['has_favorites'] = True if self.get_queryset().filter(favorite_of=self.request.user.profile).count() > 1 else False
        self.available_filters['has_visited']   = True if self.get_queryset().filter(visitors__user=self.request.user).count() > 1 else False
      return self.available_filters

  
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
    }
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
                   queryset.filter(description__icontains=q) |\
                   queryset.filter(category__name__icontains=q) |\
                   queryset.filter(additional_category__name__icontains=q) |\
                   queryset.filter(chain__name__icontains=q) |\
                   queryset.filter(chain__parent__name__icontains=q) |\
                   queryset.filter(tags__name__icontains=q) |\
                   queryset.filter(location__name__icontains=q) |\
                   queryset.filter(location__parent__name__icontains=q) |\
                   queryset.filter(location__parent__parent__name__icontains=q)
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
    queryset = queryset.order_by('location__parent__parent', 'location__parent', 'location__name').distinct()
    self.cached_queryset = queryset
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope']            = self.get_scope()
    ''' Fetch Active Filters '''
    context['active_filters']   = self.get_active_filters()
    context['available_filters']= self.get_available_filters()
    return context
  

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