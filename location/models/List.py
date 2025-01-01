from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe

from .base_model import BaseModel
from .Location import Location
from .Media import Media

from math import floor
from datetime import datetime
import googlemaps


def plural(counter, options):
  if counter == 1:
    return options[0]
  else:
    if len(options) == 1:
      return f"{ options[0] }s"
    else:
      return options[1]
    
def secondsToReadableTime(seconds):
  time = []
  ''' Exceptions: less than a minute '''
  if seconds == 0:
    return _('unknown')
  elif seconds < 60:
    return _('under one minute')
  ''' Start with the biggest numbers '''
  if seconds >= 60*60*24*7*52:
    years = floor(seconds/(60*60*24*7*52))
    time.append(f"{ str(years) } {_(plural(years, ('year', 'years')))}")
    seconds = seconds - (years * (60*60*24*7*52))
  if seconds >= 60*60*24*7:
    weeks = floor(seconds/(60*60*24*7))
    time.append(f"{ str(weeks) } {_(plural(weeks, ('week', 'weeks')))}")
    seconds = seconds - (weeks * (60*60*24*7))
  if seconds >= 60*60*24:
    days = floor(seconds/(60*60*24))
    time.append(f"{ str(days) } {_(plural(days, ('day', 'days')))}")
    seconds = seconds - (days * (60*60*24))
  if seconds >= 60*60:
    hours = floor(seconds/(60*60))
    time.append(f"{ str(hours) } {_(plural(hours, ('hour', 'hours')))}")
    seconds = seconds - (hours * (60*60))
  if seconds >= 60:
    minutes = floor(seconds/(60))
    time.append(f"{ str(minutes) } {_(plural(minutes, ('minute', 'minutes')))}")
    seconds = seconds - (minutes * (60))
  return ', '.join(time)

def secondsToTime(seconds):
  time = []
  ''' Exceptions: less than a minute '''
  if seconds == 0:
    return _('unknown')
  elif seconds < 60:
    return _('under one minute')
  ''' Start with the biggest numbers '''
  if seconds >= 60*60*24:
    days = floor(seconds/(60*60*24))
    time.append(f"{ str(days) }d ")
    seconds = seconds - (days * (60*60*24))
  if seconds >= 60*60:
    hours = floor(seconds/(60*60))
    seconds = seconds - (hours * (60*60))
    minutes = round(seconds / 600)*10
    
    time.append(f"{ '0' if hours < 10 else '' }{ str(hours) }h{ '0' if len(str(minutes)) <= 1 else '' }{ str(minutes) }m")
    # time.append(f"{ '0' if hours < 10 else '' }{ str(hours) }:{ '0' if floor(seconds/60) < 10 else '' }{ str(floor(seconds/60)) }")
  elif seconds >= 60:
    minutes = floor(seconds/(60))
    time.append(f"{ str(minutes) }m")
    seconds = seconds - (minutes * (60))
  return ''.join(time)

def metersToKilometers(meters):
  if meters == 0:
    return _('unknown')
  if meters < 1000:
    return _('under 1 km')
  return f"{ str(floor(meters/100)/10) } km"


class List(BaseModel):
  ''' Internal Identifier '''
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")

  ''' Location information '''
  name                = models.CharField(max_length=255, help_text=_('Name of location as it is identified by'))
  description         = models.TextField(blank=True, help_text=_('Markdown is supported'))
  
  ''' Is Editable '''
  is_editable         = models.BooleanField(default=True, help_text=_('should this list appear at locations when adding a location to a list'))
  ''' Template options '''
  template_choices = (
      ('l', _('list')),
      ('t', _('trip')),
  )
  template            = models.CharField(max_length=1, choices=template_choices, default='t')
    
  ''' Map option '''
  map                 = models.BooleanField(default=False, help_text=_('Show map on list page'))

  class Meta:
    verbose_name = _("list")
    verbose_name_plural = _("lists")

  def __str__(self):
    return f"{ self.name } { _('by') } { self.user.get_full_name() if self.user.get_full_name() else self.user.username }"

  def get_absolute_url(self):
    return reverse_lazy("location:list", kwargs={"slug": self.slug})
  
  def getFilteredLocations(self):
    return ListLocation.objects.filter(list__id=self.id, status='p')

  def getDistance(self):
    distance = 0
    for location in self.location.all():
      if location.getDistanceToPrevious():
        distance += location.getDataToPrevious().distance
    return metersToKilometers(distance)
  
  def getTime(self):
    time = 0
    for location in self.location.all():
      if location.getDistanceToPrevious():
        time += location.getDataToPrevious().time
    return secondsToTime(time)
  
  def getNights(self):
    return self.location.aggregate(Sum('nights'))['nights__sum']
  
  def getPrice(self):
    return self.location.aggregate(Sum('price'))['price__sum']

class ListLocation(BaseModel):
  list                = models.ForeignKey(List, related_name='locations', on_delete=models.CASCADE)
  location            = models.ForeignKey(Location, related_name='list', on_delete=models.CASCADE)
  order               = models.IntegerField(default=0)

  comment             = models.TextField(blank=True, help_text=_('Markdown is supported'))
  nights              = models.IntegerField(default=0)
  price               = models.IntegerField(default=0)

  media               = models.ForeignKey(Media, on_delete=models.DO_NOTHING, blank=True, null=True)

  ''' When List has Map set to True, show this location in the route '''
  show_on_route       = models.BooleanField(default=True) 
  

  class Meta:
    verbose_name = _("list-location")
    verbose_name_plural = _("list-locations")
    ordering          = ['list', 'order']
    get_latest_by     = ['order']


  def __str__(self):
    return f"{ self.location } { _('in') } { self.list }"

  def get_absolute_url(self):
    return reverse_lazy("location:list", kwargs={"slug": self.list.slug})

  def getPrevious(self):
    return ListLocation.objects.filter(list=self.list, order__lte=self.order).exclude(pk=self.pk).filter(status='p').last()
  def getNext(self):
    return ListLocation.objects.filter(list=self.list, order__gte=self.order).exclude(pk=self.pk).filter(status='p').first()
  def getPreviousLocation(self):
    return ListLocation.objects.filter(list=self.list, order__lte=self.order).exclude(pk=self.pk).filter(status='p').exclude(location__category__parent__slug='activity').last()
  def getNextLocation(self):
    return ListLocation.objects.filter(list=self.list, order__gte=self.order).exclude(pk=self.pk).filter(status='p').exclude(location__category__parent__slug='activity').first()
  
  def getDataToPrevious(self):
    if self.getPrevious():
      data = ListDistance.objects.filter(origin__slug=self.getPrevious().location.slug, destination__slug=self.location.slug).last()
      return data
  def getDistanceToPrevious(self):
    if self.getDataToPrevious():
      return self.getDataToPrevious().getDistance()
  def getTimeToPrevious(self):
    if self.getDataToPrevious():
      return self.getDataToPrevious().getTime()
  def getShortTimeToPrevious(self):
    if self.getDataToPrevious():
      return self.getDataToPrevious().getShortTime()

  def getDataToPreviousLocation(self):
    if self.getPreviousLocation():
      data = ListDistance.objects.filter(origin__slug=self.getPreviousLocation().location.slug, destination__slug=self.location.slug).last()
      return data
  def getDistanceToPreviousLocation(self):
    if self.getDataToPreviousLocation():
      return self.getDataToPreviousLocation().getDistance()
  def getTimeToPreviousLocation(self):
    if self.getDataToPreviousLocation():
      return self.getDataToPreviousLocation().getTime()
  def getShortTimeToPreviousLocation(self):
    if self.getDataToPreviousLocation():
      return self.getDataToPreviousLocation().getShortTime()

class ListDistance(models.Model):
  origin              = models.ForeignKey(Location, related_name='dest_origin', on_delete=models.CASCADE)
  destination         = models.ForeignKey(Location, related_name='dest_destination', on_delete=models.CASCADE)
  
  distance            = models.BigIntegerField(default=0, help_text='in meters')
  time                = models.BigIntegerField(default=0, help_text='in seconds')

  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='listdistances')

  def __str__(self):
    
    return f"{ self.origin } -> { self.destination }: { self.getDistance() }km, { self.getTime() }"
  
  def hasData(self):
    if not self.distance and not self.time:
      return False
    return True

  def getDistance(self):
    if self.distance == 0:
      return _('unknown')
    if self.distance < 1000:
      return _('under 1 km')
    return f"{ str(floor(self.distance/100)/10) } km"
  
  def getTime(self):
    return secondsToReadableTime(self.time)
  def getShortTime(self):
    return secondsToTime(self.time)

  def getData(self, request=None):
    ''' Ensure lat and lng are stored of the current location '''
    for location in (self.origin, self.destination):
      if not location.coord_lat or not location.coord_lng:
        location.getLatLng(request=request)
    ''' Fetch route information from origin to destination from Google '''
    gmaps = googlemaps.Client(key=settings.GOOGLE_API_KEY)
    now = datetime.now()
    ''' Store Origin and Destination '''
    origin      = f"{ self.origin.coord_lat },{ self.origin.coord_lng}"
    destination = f"{ self.destination.coord_lat },{ self.destination.coord_lng}"
    ''' Fetch Driving Instructions from Google '''
    try: 
      directions = gmaps.directions(origin,
                                    destination,
                                    mode='driving',
                                    traffic_model='optimistic',
                                    units='metric',
                                    departure_time=now)
    except Exception as e:
      message = f"Error when talking to Google for \"{ str(self) }\": <br />{ e }"
      if request:
        messages.add_message(request, messages.ERROR, mark_safe(message))
      return message
    # messages.add_message(request, messages.INFO, mark_safe(f"<pre>{ directions }</pre>"))
    ''' Process relevant information from directon response '''
    self.distance = directions[0]['legs'][0]['distance']['value']
    self.time = directions[0]['legs'][0]['duration']['value']
    self.save()
    messages.add_message(request, messages.INFO, f"Stored route information for route { self.origin } to { self.destination }: distance { self.getDistance() } km, time: { self.getTime() }")
