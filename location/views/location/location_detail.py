from django.views.generic.list import ListView

from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings

from ..snippets.filter_class import FilterClass
from ..snippets.order_media import order_media

from location.models.Location import Location, Category, Chain, Link
from location.models.Comment import Comment
from location.models.Tag import Tag
from location.models.List import List, ListLocation
from location.models.Profile import VisitedIn
from location.models.Media import Media

''' Location Detail View '''


class LocationView(ListView, FilterClass):
  ''' Location View 
      The location view loads all information about the location and displays this to the user.
      The location view is built around the Comment model. This allows for the comments to be
      paginated within the location, since the amount of comments can greatly exceed the amount 
      of location.
  '''
  model = Comment
  paginate_by = settings.PAGINATE
  template_name = 'location/location_detail.html'

  ''' Get Location
      Use Slug from URL to identify location. If not found, trigger a 404
  '''

  def get_location(self):
    if not hasattr(self, 'location'):
      self.location = Location.objects.get(slug=self.kwargs['slug'])
    return self.location

  ''' Queryset 
      Get Comments for selected location
  '''

  def get_queryset(self):
    queryset = Comment.objects.filter(location__slug=self.get_location().slug)
    queryset = self.filter_status(queryset)
    queryset = self.filter_visibility(queryset)
    return queryset.order_by('-date_added').distinct()

  ''' Context Data
      Most information in this view is stowed away in the Context Data.
  '''

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Location: use self.get_location() to return the location '''
    location = self.get_location()
    context['location'] = location
    ''' Scope '''
    context['scope'] = f"{ _(location.getCategory()) }: { location.name }"
    ''' Tags 
        Fetch tags in seperate query to be able to filter the tags for status and visibility
    '''
    context['tags'] = self.get_tags()
    ''' Lists 
        Fetch Lists in seperate query to be able to filter for status and visibility
    '''
    context['lists'] = self.get_lists()
    ''' Available lists
        Fetch a queryset of lists where this location is not mentioned in
    '''
    context['available_lists'] = self.get_available_lists()
    ''' User dependant functions '''
    if self.request.user.is_authenticated:
      context['has_bucketlist'] = True if List.objects.filter(name='Bucketlist', user=self.request.user).count() > 0 else False
      context['distance_to_home'] = self.get_distance_to_home()
    ''' Visits '''
    if location.visibility == 'f':
      if hasattr(location.user, 'profile'):
        context['family'] = location.user.profile.family.all()
    ''' Nearby '''
    context['nearby_locations'] = self.get_nearby()
    context['visitors'] = self.get_visitors()
    ''' Media '''
    context['media'] = self.get_media()
    return context

  ''' Get Tags
  '''

  def get_tags(self):
    tags = Tag.objects.filter(locations__slug=self.get_location().slug)
    tags = self.filter_status(tags)
    tags = self.filter_visibility(tags)
    tags = tags.order_by('list_as', 'name').distinct()
    return tags
  
  ''' Get Lists 
      Returns a queryset of lists this location is mentioned in
  '''
  def get_lists(self):
    lists = ListLocation.objects.filter(
        list__status='p', location=self.get_location())
    lists = self.filter_status(lists)
    lists = self.filter_visibility(lists)
    lists = lists.order_by('list__name').distinct()
    return lists

  def get_available_lists(self):
    ''' Build a list of lists based on ListLocations that the current location is in.
        This allows to filter out removed listlocations, and keep only lists where the location
        is mentioned in.
    '''
    listlocations = ListLocation.objects.filter(location=self.get_location())
    listlocations = self.filter(listlocations)
    listlocations = listlocations.values_list('list__slug', flat=True)
    ''' Lists the location is mentioned in should be removed from available lists, to avoid
        double entries.
    '''
    available_lists = List.objects.exclude(slug__in=listlocations)
    available_lists = self.filter_status(available_lists)
    available_lists = self.filter_visibility(available_lists)
    available_lists = available_lists.order_by().distinct()
    return available_lists

  ''' Get Visitors '''
  def get_visitors(self):
    if self.request.user.is_authenticated:
      result = VisitedIn.objects.filter(
          user=self.request.user, location=Location.objects.get(slug=self.kwargs['slug']))
      result = self.filter_visibility(result)
      return result

  ''' Get nearby '''
  def get_nearby(self):
    all_locations = Location.objects.exclude(pk=self.get_location().id)
    all_locations = self.filter_status(all_locations)
    all_locations = self.filter_visibility(all_locations)
    nearby_locations = []
    from geopy.distance import geodesic
    for location in all_locations:
      distance = geodesic((self.get_location().coord_lat, self.get_location(
      ).coord_lng), (location.coord_lat, location.coord_lng)).kilometers
      if distance <= settings.NEARBY_RANGE:
        nearby_locations.append((location, distance))
    nearby_locations.sort(key=lambda x: x[1])
    return nearby_locations

  ''' Get media '''
  def get_media(self):
    media = Media.objects.filter(location=self.get_location())
    media = self.filter_status(media)
    media = self.filter_visibility(media)
    media = order_media(media)
    return media

  ''' Get distance to home '''
  def get_distance_to_home(self):
    if self.request.user.is_authenticated:
      result = False
      for distance in self.get_location().dest_origin.all():
        if distance.destination == self.request.user.profile.home:
          result = distance      
      for distance in self.get_location().dest_destination.all():
        if distance.origin == self.request.user.profile.home:
          result = distance
      return result
    return None