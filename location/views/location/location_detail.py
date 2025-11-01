from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from django.utils.translation import gettext as _
from django.conf import settings
from django.shortcuts import redirect
from django.http import Http404

# from ..snippets.filter_class import FilterClass
from ..snippets.order_media import order_media
from cmnsd.views.cmnsd_filter import FilterMixin

from location.models.Location import Location, Link, Description, Size
from location.models.Comment import Comment
from location.models.Tag import Tag
from location.models.List import List, ListLocation
from location.models.Profile import VisitedIn
from location.models.Media import Media



''' Location Detail View '''


class LocationView(FilterMixin, DetailView):
  ''' Location View 
      The location view loads all information about the location and displays this to the user.
      The location view is built around the Comment model. This allows for the comments to be
      paginated within the location, since the amount of comments can greatly exceed the amount 
      of location.
  '''
  model = Location
  template_name = 'location/location/location_detail.html'

  ''' Context Data
      Most information in this view is stowed away in the Context Data.
  '''

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Location: use self.get_location() to return the location '''
    ''' Scope '''
    context['scope'] = f"{ _(self.get_object().getCategory()) }: { self.get_object().name }"
    ''' Lists 
        Fetch Lists in seperate query to be able to filter for status and visibility
    '''
    context['lists'] = self.get_lists()
    ''' User dependant functions '''
    if self.request.user.is_authenticated:
      context['visited_locations'] = self.request.user.visits.filter(status='p').values_list("location_id", flat=True)
    ''' Nearby '''
    # context['nearby_locations'] = self.get_nearby(settings.NEARBY_RANGE)
    context['map_locations'] = self.get_nearby(settings.MAP_RANGE)
    # context['visitors'] = self.get_visitors()
    ''' Media '''
    context['media'] = self.get_media()
    ''' Maps '''
    context['maps_permission'] = self.get_maps_permission()
    context['ajax'] = {
      'editable': True if 'editable' in self.request.GET else False,
    }
    return context

  ''' Get Lists 
      Returns a queryset of lists this location is mentioned in
  '''
  def get_lists(self):
    lists = ListLocation.objects.filter(
        list__status='p', location=self.get_object())
    lists = self.filter_status(lists)
    lists = self.filter_visibility(lists)
    lists = lists.order_by('list__name').distinct()
    return lists

  ''' Get nearby '''
  def get_nearby(self, range=settings.NEARBY_RANGE):
    all_locations = Location.objects.exclude(pk=self.get_object().id)
    all_locations = self.filter_status(all_locations)
    all_locations = self.filter_visibility(all_locations)
    nearby_locations = []
    from geopy.distance import geodesic
    for location in all_locations:
      distance = geodesic((self.get_object().coord_lat, self.get_object().coord_lng), (location.coord_lat, location.coord_lng)).kilometers
      if distance <= range:
        nearby_locations.append((location, distance))
    nearby_locations.sort(key=lambda x: x[1])
    return nearby_locations

  ''' Get media '''
  def get_media(self):
    media = Media.objects.filter(location=self.get_object())
    media = self.filter_status(media)
    media = self.filter_visibility(media)
    media = order_media(media)
    return media

  ''' Get distance to home 
      Check if the distance from or to home is stored, and if so 
      return the value.
      This means that if a distance was stored in creating a list, of 
      by another user, the same distance is used. 
      If no distance is known, return Null
  '''
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


class ShortLocationUrlView(DetailView):
  ''' Short Location URL View
      This view handles short URLs for locations, redirecting to the full location detail page.
      Example: /loc/short-slug/ redirects to /location/long-slug/
  '''
  model = Location
  
  def get_object(self, queryset = ...):
    try:
      object = Location.objects.get(token=self.kwargs['token'])
      return object
    except Location.DoesNotExist:
      raise Http404

  def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    return redirect(self.object.get_absolute_url())