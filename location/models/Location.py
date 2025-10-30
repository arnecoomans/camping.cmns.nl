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

from html import escape
from urllib.parse import urlparse
from geopy import distance, exc
from geopy.geocoders import GoogleV3
from geopy.distance import geodesic

from cmnsd.models.cmnsd_basemodel import BaseModel, VisibilityModel
from cmnsd.models.cmnsd_basemethod import ajax_function
from cmnsd.views.cmnsd_filter import FilterMixin

# from .base_model import BaseModel
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

  def get_absolute_url(self):
    return reverse_lazy('location:locations') + f"?chain={ self.slug }"
  
''' Links model
    Any location may have multiple links related to the location, such as several review websites
'''
class Link(VisibilityModel,BaseModel):
  name                = models.CharField(max_length=255, blank=True, help_text=_('Title of link, optional'))
  url                 = models.CharField(max_length=512, unique=True, help_text=_('full url of link'))
  primary             = models.BooleanField(default=False, help_text=_('primary link for location'))  

  def __str__(self) -> str:
    return self.get_title()

  def get_title(self):
    if self.name:
      return self.name
    hostname = self.hostname()
    if 'google' in hostname:
      ''' Google Maps results 
          Return the search query as title
          Search query is the string after /maps/search/
      '''
      if 'maps/' in self.url:
        query = self.url.split('/')
        counter = 0
        for q in query:
          if 'search' in q:
            query = query[counter+1].replace('+', ' ').capitalize()
            break
          counter += 1
        query = query if len(query) > 0 else _('search')
        return f"{ query } on { hostname.capitalize() } Maps"
      ''' Google search results 
          Return the search query as title
          Search query is the string after ?q=    
      '''
      query = urlparse(self.url).query
      query = query.split('&')
      for q in query:
        if 'q=' in q:
          query = q.replace('q=', '')
          break
      query = query if str(query) != "['']" else _('search').capitalize()
      return f"{ query } on { hostname.capitalize() }"
    return hostname
  
  def save(self, *args, **kwargs):
    ''' Enforce URL to be correct '''
    if not self.url.startswith('http://') and not self.url.startswith('https://'):
      self.url = f"https://{ self.url }"
    return super(Link, self).save(*args, **kwargs)
    
  def hostname(self):
    if urlparse(self.url).hostname:
      return urlparse(self.url).hostname.replace('www.', '')
    elif self.url:
      return self.url
    return _('no url')
  
  class Meta:
        ordering = ['-primary', 'url']

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
    ordering = ['parent__name', 'name']

  def __str__(self) -> str:
    if self.parent:
      return f"{ self.parent.name }: { self.name }"
    return self.name
  
  def get_absolute_url(self):
    return reverse_lazy('location:locations') + f"?category={ self.slug }"
  
  js_template_name = 'categories'


''' Description Model '''
class Description(VisibilityModel, BaseModel):
  description         = models.TextField(blank=True, help_text=_('Markdown is supported'))
  location            = models.ForeignKey('Location', related_name='descriptions', on_delete=models.CASCADE)

  def __str__(self) -> str:
    return self.description
  
  def locs(self):
    return self.locations.all()
  class Meta:
    # 👇 ensure it's concrete
    abstract = False
    ordering = ['-date_created']
    unique_together = ('location', 'visibility')

class Size(BaseModel):
  slug              = models.CharField(max_length=255, help_text=_('Slug of size'))
  name              = models.CharField(max_length=255, unique=True, help_text=_('Name of size as displayed'))
  description       = models.TextField(blank=True, help_text=_('Markdown is supported'))

  def __str__(self):
    return self.name
  
''' Location model
'''
class Location(FilterMixin, VisibilityModel,BaseModel):
  ''' Internal Identifier '''
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")

  ''' Location information '''
  name                = models.CharField(max_length=255, help_text=_('Name of location as it is identified by'))
  address             = models.CharField(max_length=512, blank=True, help_text=_('Full street address of location, including as much information as possible, such as city, region, country'))
  phone               = models.CharField(max_length=32, null=True, blank=True)
  owners_names        = models.CharField(max_length=255, blank=True, help_text=_('Name of owner(s), if known'))

  # description         = models.TextField(blank=True, help_text=_('Markdown is supported'))
  # descriptions        = models.ManyToManyField(Description, blank=True, related_name='locations')

  links               = models.ManyToManyField(Link, blank=True, help_text=_('Add links to related websites, such as blogs refering to this location or review websites'))
  chains              = models.ManyToManyField(Chain, blank=True, related_name='locations')

  ''' Categorisation '''
  category            = models.ForeignKey(Category, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='locations')
  additional_category = models.ManyToManyField(Category, blank=True, related_name='secondary_for')
  tags                = models.ManyToManyField(Tag, blank=True, related_name='locations')
  size                = models.ForeignKey(Size, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='locations')
  ''' Augmented Information '''
  meta_description    = models.CharField(max_length=255, blank=True, help_text=_('Meta description taken from website, if available'))

  distance_to_departure_center = models.BigIntegerField(null=True, blank=True, help_text=f"{ _('distance to central location in departure region')} { _('in kilometers') }")

  location            = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True, related_name='locations')
  coord_lat           = models.CharField(max_length=64, blank=True, editable=False, help_text=f"{ _('Coordinates') }: Lat ({ _('fetched from location service based on name and/or address') })")
  coord_lng           = models.CharField(max_length=64, blank=True, editable=False, help_text=f"{ _('Coordinates') }: Lng ({ _('fetched from location service based on name and/or address') })")

  ''' Data Cache '''
  automated_changelog = models.TextField(editable=False, blank=True)
  cached_google       = models.JSONField(null=True, editable=False)
  
  ''' Object Meta Functions '''
  def __str__(self) -> str:
    return self.name
  
  class Meta:
    ordering = ['name']
  
  def get_absolute_url(self):
    if self.isActivity():
      return reverse_lazy('location:activity', kwargs={'slug': self.slug })  
    else:
      return reverse_lazy('location:location', kwargs={'slug': self.slug })  

  def save(self, *args, **kwargs):
    if self.category == 'home':
      self.status = '-'
    # Calculate average distance to center for region
    if self.location:
      self.location.calculate_average_distance_to_center()
    return super(Location, self).save(*args, **kwargs)

  @ajax_function
  def nearby(self, request=None, range=None):
    range = range if range else getattr(settings, 'NEARBY_RANGE', 50)
    all_locations = Location.objects.exclude(pk=self.id)
    all_locations = self.filter(all_locations, request=request, suppress_search=True)
    # all_locations = self.filter_visibility(all_locations)
    nearby_locations = []
    
    for location in all_locations:
      distance = geodesic((self.coord_lat, self.coord_lng), (location.coord_lat, location.coord_lng)).kilometers
      if distance <= range:
        nearby_locations.append((location, distance))
    nearby_locations.sort(key=lambda x: x[1])
    return [x[0] for x in nearby_locations]

  ''' Data Access Functions '''
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
    if len(self.address) > 0:
      return self.address
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
    if hasattr(location, 'address') and location != None:
      self.addToChangelog(f"Changed address from { self.address } to { location.address }")
      self.address = location.address
      ''' Report progess '''
      message = f"Stored address { self.address } of { self.name }."
    else:
      message = f"Could not fetch address of { self.name }"
    self.save()
    
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
      if not self.coord_lat or not self.coord_lng:
        self.distance_to_departure_center = None
        return None
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
    message = None
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
    if location:
      self.cached_google = location.raw
      self.save()
      data = self.extract_address_parts(location)
      country         = data['country']
      country_slug    = data['country_slug']
      region          = data['region']
      region_slug     = data['region_slug']
      department      = data['department']
      department_slug = data['department_slug']
      # for field in location.raw['address_components']:
      #   if 'country' in field['types']:
      #     country = field['long_name']
      #     country_slug = field['short_name']
      #   elif 'administrative_area_level_1' in field['types']:
      #     region = field['long_name']
      #     region_slug = field['short_name']
      #   elif 'sublocality_level_1' in field['types']:
      #     region = field['long_name']
      #     region_slug = field['short_name']
      #   elif 'administrative_area_level_2' in field['types']:
      #     department = field['long_name']
      #     department_slug = field['short_name']
      #   elif 'administrative_area_level_3' in field['types']:
      #     department = field['long_name']
      #     department_slug = field['short_name']
      #   elif 'locality' in field['types'] and 'political' in field['types']:
      #     department = field['long_name']
      #     department_slug = field['short_name']
        
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
    else:
      ''' If address is not found, display a warning '''
      if request:
        messages.add_message(request, messages.WARNING,
                             f"{ _('did not detect address of') } { self.name } { _('so cannot detect region') }")
    if request:
      messages.add_message(request, messages.INFO, message)
    else:
      return message
  
  def extract_address_parts(self, location):
    """Extract structured address info (country, region, department) from Google Maps `address_components`."""
    from django.conf import settings

    components = location.raw.get('address_components', [])
    if not components:
      raise ValueError("Location has no address_components in raw data.")

    # Define mapping of Google types → your internal logical fields
    mapping = {
      'country': ('country', 'country_slug'),
      # Regions:
      'administrative_area_level_1': ('region', 'region_slug'),
      'sublocality_level_1': ('region', 'region_slug'), 
      # Departments:
      'administrative_area_level_2': ('department', 'department_slug'),
      'administrative_area_level_3': ('department', 'department_slug'),
      'locality': ('department', 'department_slug'),
    }

    # Initialize defaults
    result = dict(
      country='(unknown)',
      country_slug='xx',
      region='(unknown region)',
      region_slug='xx',
      department='(unknown department)',
      department_slug='xx',
    )

    # Parse components
    for component in components:
      types = component.get('types', [])
      long_name = component.get('long_name', '')
      short_name = component.get('short_name', '')

      for google_type, (target_name, target_slug) in mapping.items():
        if google_type in types:
          result[target_name] = long_name
          result[target_slug] = short_name

    # Log missing info for debug visibility
    if getattr(settings, 'DEBUG', False):
      missing = [k for k, v in result.items() if v.startswith('(')]
      if missing:
        print(f"[DEBUG] Missing address fields for {location}: {', '.join(missing)}")

    # Optionally raise if critical fields (e.g., country) are missing
    if result['country'] == '(unknown)':
      raise ValueError(
        f"Could not detect country in address_components for location '{getattr(location, 'name', '?')}'. "
        "Expected a 'country' field in Google response."
      )

    return result
  ''' Quick access to Country, Region and Department '''
  def __get_region_info(self):
    data = {
      'country': None,
      'region': None,
      'department': None
    }
    ''' If location has no parent, location is country '''
    if self.location:
      if not self.location.parent:
        data['country'] = self.location
      if self.location.parent:
        if not self.location.parent.parent:
          data['country'] = self.location.parent
          data['region'] = self.location
        if self.location.parent.parent:
          data['country'] = self.location.parent.parent
          data['region'] = self.location.parent
          data['department'] = self.location
    return data

  def country(self):
    return self.__get_region_info()['country']
    
  def region(self):
    return self.__get_region_info()['region']
  
  def department(self):
    return self.__get_region_info()['department']
    
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
  # Hybrid workaround to make activity field accessible as a property
  # while maintaining the ability to use the original method in query filter
  @property
  def is_activity(self):
    return self.isActivity()
  @property
  def is_location(self):
    return not self.isActivity()
  
  def getCategory(self):
    if self.isActivity():
      return settings.ACTIVITY_SLUG
    return 'location'
  def getPCategory(self):
    if self.isActivity():
      return 'activities'
    return 'locations'
  
  def canhavesize(self):
    ''' Determine if a location can have a size, based on category '''
    categories = getattr(settings, 'LOCATION_SIZE_CATEGORIES', ['camping', 'glamping', 'transit'])
    canhavesize = False
    if self.category.slug.lower() in categories:
      canhavesize = True
    for category in self.additional_category.all():
      if category.slug.lower() in categories:
        canhavesize = True
    return canhavesize
  
  def availablesizes(self):
    ''' Return a queryset of sizes that are applicable for this location '''
    if self.canhavesize():
      return Size.objects.all().order_by().distinct()
    return Size.objects.none()
  
  def get_available_description_visibilities(self):
    visibilities = {}
    for key, label in Description.visibility.field.choices:
      if not Description.objects.filter(location=self, visibility=key).exists():
        visibilities[key] = label
    return visibilities