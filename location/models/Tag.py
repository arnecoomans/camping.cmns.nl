from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as __
from django.utils.text import slugify

from django.urls import reverse_lazy

from cmnsd.models.cmnsd_basemodel import BaseModel, VisibilityModel
from cmnsd.models.Tag import Tag
# from .base_model import BaseModel

class Tag(VisibilityModel,Tag):
  # slug                = models.CharField(max_length=64, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")
  # name                = models.CharField(max_length=128, help_text=_('Name of tag'))
  # parent              = models.ForeignKey("self", on_delete=models.CASCADE, related_name='children', null=True, blank=True)

  list_as_choices     = (
    ('n', __('Tag is advantage or disadvantage', 'neither')),
    ('a', __('Tag is advantage or disadvantage', 'advantage')),
    ('d', __('Tag is advantage or disadvantage', 'disadvantage')),
    ('b', __('Tag is advantage or disadvantage', 'both')),
  )
  list_as             = models.CharField(max_length=1, choices=list_as_choices, default='b')
  hide_from_filterlist = models.BooleanField(default=False)

  class Meta:
    ordering = ['-list_as', 'name']
    # constraints = [
    #   models.UniqueConstraint(fields=['parent', 'name'], name='unique_name_per_parent')
    # ]

  # def __str__(self) -> str:
  #   return self.display_name()
  
  def get_absolute_url(self):
    return reverse_lazy('location:tag', args=[self.slug])
  
  # def save(self, *args, **kwargs):
  #   if not self.name and self.slug:
  #     self.name = self.slug.replace('-', ' ').replace('_', ' ').replace('+', ' ').title()
  #   if not self.slug and self.name:
  #     self.slug = slugify(self.name)
  #   super().save(*args, **kwargs)

  # def display_name(self) -> str:
  #   name = ''
  #   if self.parent:
  #     name += self.parent.name + ': '
  #   name += self.name
  #   return name

  def getLocations(self):
    result = []
    for location in self.locations.all():
      if not location.isActivity():
        result.append(location)
    return result
  
  def getActivities(self):
    result = []
    for location in self.locations.all():
      if location.isActivity():
        result.append(location)
    return result