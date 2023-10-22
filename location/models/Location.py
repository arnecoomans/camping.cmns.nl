''' Location model
    Describes possible locations to stay overnight during a trip. 
'''

from datetime import datetime

from django.db import models
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse_lazy


from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


from geopy import distance, exc
from geopy.geocoders import Nominatim, GoogleV3


from .base_model import BaseModel
from .Geo import Region
from .Tag import Tag

''' Location Chain model
    When a location is part of a chain (mother company), it can be useful to locate other locations by the 
    same chain. Since often services and level of quality are alike. 
'''
class Chain(models.Model):
  ''' Internal Identifier '''
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")

  ''' Location information '''
  name                = models.CharField(max_length=255, help_text=_('Name of location as it is identified by'))
  website             = models.CharField(max_length=512, blank=True, help_text=_('Full website address of location'))
  description         = models.TextField(blank=True, help_text=_('Markdown is supported'))

  parent              = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='children')

  ''' Record Meta information '''
  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING)

  def __str__(self):
    if self.parent:
      return f"{ self.name } ({ self.parent })"
    return self.name
  
''' Links model
    Any location may have multiple links related to the location, such as several review websites
'''
class Link(BaseModel):
  url                 = models.CharField(max_length=512, unique=True, help_text=_('full url of link'))

  def __str__(self) -> str:
    return self.url
  
  def hostname(self):
    # Remove http:// and https:// and split content by /
    url = self.url.replace('http://','').replace('https://','').split('/')
    # The first part should be the hostname
    hostname = url[0].replace('www.', '')
    return hostname

''' Category model
'''
class Category(models.Model):
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")
  name                = models.CharField(max_length=255, help_text=_('Name of category'))
  parent              = models.ForeignKey("self", on_delete=models.CASCADE, related_name='children', null=True, blank=True)
  
  ''' Record Meta information '''
  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING)

  class Meta:
    verbose_name_plural = 'categories'

  def __str__(self) -> str:
    if self.parent:
      return f"{ self.parent.name }: { self.name }"
    return self.name


''' Location model
'''
class Location(BaseModel):
  ''' Internal Identifier '''
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")

  ''' Location information '''
  name                = models.CharField(max_length=255, help_text=_('Name of location as it is identified by'))
  website             = models.CharField(max_length=512, blank=True, unique=True, help_text=_('Full website address of location'))
  address             = models.CharField(max_length=512, blank=True, help_text=_('Full street address of location, including as much information as possible, such as city, region, country'))
  phone               = models.CharField(max_length=32, null=True, blank=True)
  owners_names        = models.CharField(max_length=255, blank=True, help_text=_('Name of owner(s), if known'))

  description         = models.TextField(blank=True, help_text=_('Markdown is supported'))

  link                = models.ManyToManyField(Link, blank=True, help_text=_('Add links to related websites, such as blogs refering to this location or review websites'))
  chain               = models.ForeignKey(Chain, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='locations')

  ''' Categorisation '''
  category            = models.ForeignKey(Category, blank=True, null=True, on_delete=models.DO_NOTHING)
  additional_category = models.ManyToManyField(Category, blank=True, related_name='secondary_for')
  tags                = models.ManyToManyField(Tag, blank=True, related_name='locations')

  ''' Augmented Information '''
  meta_description    = models.CharField(max_length=255, blank=True, help_text=_('Meta description taken from website, if available'))

  distance_to_departure_center = models.BigIntegerField(null=True, blank=True, help_text=f"{ _('distance to central location in departure region')} { _('in kilometers') }")

  location            = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True, related_name='locations')
  coord_lat           = models.CharField(max_length=64, blank=True, editable=False, help_text=f"{ _('Coordinates') }: Lat ({ _('fetched from location service based on name and/or address') })")
  coord_lng           = models.CharField(max_length=64, blank=True, editable=False, help_text=f"{ _('Coordinates') }: Lng ({ _('fetched from location service based on name and/or address') })")

  # ''' Record Meta information '''
  # visibility_choices      = (
  #     ('p', _('public')),
  #     ('c', _('commmunity')),
  #     ('f', _('family')),
  #     ('q', _('private')),
  #   )
  # visibility          = models.CharField(max_length=1, choices=visibility_choices, default='p')
  
  # status_choices      = (
  #     ('p', _('published')),
  #     ('r', _('revoked')),
  #     ('x', _('deleted')),
  #   )
  # status              = models.CharField(max_length=1, choices=status_choices, default='p')
  # date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  # date_modified       = models.DateTimeField(editable=False, auto_now=True)
  # user                = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='locations')

  ''' Data Cache '''
  automated_changelog = models.TextField(editable=False, blank=True)
  cached_google       = models.JSONField(null=True, editable=False)
  
  ''' Object Meta Functions '''
  def __str__(self) -> str:
    return self.name
  
  class Meta:
    ordering = ['name']
  
  def get_absolute_url(self):
    return reverse_lazy('location:location', kwargs={'slug': self.slug })  

  def save(self, *args, **kwargs):
    if self.category == 'home':
      self.status = '-'
    return super(Location, self).save(*args, **kwargs)


  ''' Data Access Functions '''
  def getWebsiteHostname(self):
    if self.website:
      # Remove http:// and https:// and split content by /
      url = self.website.replace('http://','').replace('https://','').split('/')
      # The first part should be the hostname
      hostname = url[0].replace('www.', '').lower()
      ''' Special hostnames '''
      if 'google' in hostname or 'zoover' in hostname or 'booking.com' in hostname:
        hostname = f"{ self.name } on { hostname }"
      return hostname
  
  def addToChangelog(self, message):
    changelog = self.automated_changelog.split("\n")
    changelog.append(f"{ datetime.now } - { message }")
    if len(changelog) > 100:
      changelog = changelog[:-99]
    self.automated_changelog = "\n".join(changelog)
    self.save()
    
  ''' Geo Data Access '''

  ''' getAddress 
      Fetch address based on name. Uses the GoogleV3 API because this has the highest chance of
      result when supplying just a location name.
      Stores the value in address field
      Returns a textual result of the query.
  '''
  def getAddress(self, request=None):
    ''' Fetch Google Geolocation data '''
    try:
      geolocator = GoogleV3(api_key=settings.GOOGLE_API_KEY)  
      location = geolocator.geocode(f"{ self.name }")
    except exc.GeocoderQueryError as e:
      message = f"Error when fetching geodata for { self.name }: <br />{ e }"
      if request:
        messages.add_message(request, messages.ERROR, mark_safe(message))
      return message
    ''' Store address from geolocation '''
    if hasattr(location, 'address'):
      self.addToChangelog(f"Changed address from { self.address } to { location.address }")
      self.address = location.address
    else:
      self.addToChangelog(f"Could not fetch address of { self.name }")
    self.save()
    ''' Report progess '''
    message = f"Stored address { self.address } of { self.name }."
    if request:
      messages.add_message(request, messages.INFO, message)
    else:
      return message
  
  ''' getLatLng 
      Fetch coördinates based on name and address. Uses the GoogleV3 API because this has the highest chance of
      result when supplying just a location name, or location + address.
      Stores the values in the coord_lat and coord_lng fields
      Returns a textual result of the query.
  '''
  def getLatLng(self, request=None):
    ''' Ensure address is filled, if not, fetch address based on name '''
    if not self.address:
      self.getAddress(request=request)
    if not self.address:
      return False
    ''' Get geolocation data from Google'''
    try:
      geolocator = GoogleV3(api_key=settings.GOOGLE_API_KEY)
      location = geolocator.geocode(f"{ self.name }, { self.address }")
    except exc.GeocoderQueryError as e:
      message = f"Error when fetching geodata for { self.name }: <br />{ e }"
      if request:
        messages.add_message(request, messages.ERROR, mark_safe(message))
      return message
    ''' Store coordinates '''
    self.coord_lat = location.latitude
    self.coord_lng = location.longitude
    self.save()
    ''' Report success '''
    message = f"Stored coördinates of { self.name }, { self.address}: { self.coord_lat }, {self.coord_lng}."
    if request:
      messages.add_message(request, messages.INFO, message)
    else:
      return message
    
  ''' getDistanceFromDeparture
      Calculate straight line distance between two locations. Uses the GoogleV3 API because this has the highest chance of
      result when supplying just a location name, or location + address.
      Departure is configured in settings.py and should be a central location in the country of most users.
      Destination is the location from the model.
      Stores the result in the distance_to_departure_center field, that can be used to sort locations by distance.
      Returns a textual result of the query.
  '''
  def getDistanceFromDepartureCenter(self, request=None):
    ''' Ensure lat and lng are stored of the current location '''
    if not self.coord_lat or not self.coord_lng:
      self.getLatLng(request=request)
    ''' Fetch Google Geolocation data for departure '''
    try:
      geolocator = GoogleV3(api_key=settings.GOOGLE_API_KEY)
      departure = geolocator.geocode(settings.DEPARTURE_CENTER)
    except exc.GeocoderQueryError as e:
      message = f"Error when fetching geodata for { self.name }: <br />{ e }"
      if request:
        messages.add_message(request, messages.ERROR, mark_safe(message))
      return message
    ''' Calculate distance between the two locations '''
    calculated_distance = distance.distance(
      (departure.latitude, departure.longitude),
      (self.coord_lat, self.coord_lng)
    )
    ''' Store the rounded down distance in the current location '''
    self.distance_to_departure_center = round(calculated_distance.km)
    self.save()
    message = f"Distance between { settings.DEPARTURE_CENTER } ({ departure }) and { self.name }, { self.address } is { self.distance_to_departure_center } km"
    if request:
      messages.add_message(request, messages.INFO, message)
    else:
      return message
  
  ''' GetRegion
      Fetch Region information from Google and set region
      Regions are stored with parent (department -> region -> country)
      All three are walked through and created in the Region model if not exists yet. 
  '''
  def getRegion(self, request=None):
    ''' Set user '''
    user = request.user if request else self.user
    ''' Ensure address is filled, if not, fetch address based on name '''
    if not self.address:
      self.getAddress(request=request)
    ''' Get geolocation data from Google'''
    try:
      geolocator = GoogleV3(api_key=settings.GOOGLE_API_KEY)
      location = geolocator.geocode(f"{ self.name }, { self.address }")
    except exc.GeocoderQueryError as e:
      message = f"Error when fetching geodata for { self.name }: <br />{ e }"
      if request:
        messages.add_message(request, messages.ERROR, mark_safe(message))
      return message
    ''' Identify Region, department and country '''
    for field in location.raw['address_components']:
      if 'country' in field['types']:
        country = field['long_name']
        country_slug = field['short_name']
      elif 'administrative_area_level_1' in field['types']:
        region = field['long_name']
        region_slug = field['short_name']
      elif 'administrative_area_level_2' in field['types']:
        department = field['long_name']
        department_slug = field['short_name']
    ''' Check if Country, Region and Department exists '''
    countryObject, created = Region.objects.get_or_create(
        slug=slugify(country_slug),
        defaults={'name': country, 'slug': slugify(country_slug), 'user': user}
      )
    regionObject, created = Region.objects.get_or_create(
        slug=slugify(region_slug),
        defaults={'name': region, 'slug': slugify(region_slug), 'parent': countryObject, 'user': user}
      )
    departmentObject, created = Region.objects.get_or_create(
      slug=slugify(department_slug),
      defaults={'name': department, 'slug': slugify(department_slug), 'parent': regionObject, 'user': user}
    )
    ''' Store Region '''
    self.location = departmentObject
    self.save()
    ''' Report progress '''
    message = f"Stored region { regionObject.name } for { self.name }"
    if request:
      messages.add_message(request, messages.INFO, message)
    else:
      return message
  ''' Quick access to Country, Region and Department '''
  def country(self):
    if self.location:
      if self.location.parent:
        if self.location.parent.parent:
          return self.location.parent.parent.name
    return None
  def countryslug(self):
    if self.location:
      if self.location.parent:
        if self.location.parent.parent:
          return self.location.parent.parent.slug
    return None
  def region(self):
    if self.location:
      if self.location.parent:
        return self.location.parent.name
    return None
  def regionslug(self):
    if self.location:
      if self.location.parent:
        return self.location.parent.slug
    return None
  def department(self):
    if self.location:
      return self.location.name
    return None
  def departmentslug(self):
    if self.location:
      return self.location.slug
    return None
  
  ''' Activity or Location logic '''
  def isActivity(self):
    if not self.category:
      return False
    elif self.category.slug.lower() == settings.ACTIVITY_SLUG:
      return True
    elif self.category.parent:
      if self.category.parent.slug.lower() == settings.ACTIVITY_SLUG or self.category.slug.lower() == settings.ACTIVITY_SLUG:
        return True
    return False
  def getCategory(self):
    if self.isActivity():
      return settings.ACTIVITY_SLUG
    return 'location'
  def getPCategory(self):
    if self.isActivity():
      return 'activities'
    return 'locations'