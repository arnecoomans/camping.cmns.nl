''' Geo Model(s)
    Stores Geographic details such as Region for later reference
'''
from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy as _

class Region(models.Model):
  ''' Internal Identifier '''
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")
  
  name                = models.CharField(max_length=255)
  parent              = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
  
  order               = models.PositiveIntegerField(default=0, help_text=f"{ _('add order to countries for sorting in distance sorted overview') }. { _('only works for countries') }")

  cached_average_distance_to_center = models.FloatField(null=True, blank=True, editable=False, help_text=f"{ _('cached average distance to center of this region') } ({ _('in km') })")

  # Meta-information
  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING)

  def __str__(self) -> str:
    if self.parent:
      return ', '.join([str(self.name), str(self.parent)])
    return self.name
  
  class Meta:
    ordering = ['name']

  def calculate_average_distance_to_center(self):
    ''' Calculate the average distance to the center of this region
        and store it in the cached_average_distance_to_center field
    '''
    locations = self.locations.all()
    if locations.exists():
      total_distance = sum([loc.distance_to_departure_center for loc in locations if loc.distance_to_departure_center is not None])
      average_distance = total_distance / locations.count()
      self.cached_average_distance_to_center = average_distance
      self.save(update_fields=['cached_average_distance_to_center'])
    regions = self.children.all()
    if regions.exists():
      total_distance = sum([reg.cached_average_distance_to_center for reg in regions if reg.cached_average_distance_to_center is not None])
      average_distance = total_distance / regions.count()
      self.cached_average_distance_to_center = average_distance
      self.save(update_fields=['cached_average_distance_to_center'])
    # For location parent, calculate the average distance
    if self.parent:
      self.parent.calculate_average_distance_to_center()
    return self.cached_average_distance_to_center
