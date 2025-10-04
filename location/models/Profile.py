from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

from django.utils.translation import gettext_lazy as _

from cmnsd.models.cmnsd_basemodel import BaseModel, VisibilityModel
#from .base_model import BaseModel
from .Location import Location
from .Tag import Tag

class NavigationApps(models.Model):
  slug = models.SlugField(max_length=50, unique=True)
  name = models.CharField(max_length=100)
  url_format = models.CharField(max_length=200, help_text=_('Use {address} as placeholder'))
  default_enabled = models.BooleanField(default=True)
  class Meta:
    verbose_name = _("Navigation app")
    verbose_name_plural = _("Navigation apps")
  def __str__(self):
    return self.name

class Profile(models.Model):
  user                = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='profile', unique=True)

  notes               = models.TextField(blank=True, help_text=_('personal notes'))
  
  home                = models.ForeignKey(Location, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='home_of')
  family              = models.ManyToManyField(User, blank=True, help_text=_('family members'), related_name='family_of')

  navigationapps      = models.ManyToManyField(NavigationApps, blank=True, related_name='profiles')

  order_choices      = (
      ('distance', _('distance')),
      ('region', _('region')),
      ('date_added', _('date added')),
      ('date_modified', _('date modified')),
    )
  order               = models.CharField(max_length=16, choices=order_choices, default=settings.DEFAULT_ORDER)
  favorite            = models.ManyToManyField(Location, blank=True, related_name='favorite_of')
  dislike             = models.ManyToManyField(Location, blank=True, related_name='least_liked_of')
  ignored_tags        = models.ManyToManyField(Tag, blank=True, related_name='ignored_by')
  
  hide_least_liked    = models.BooleanField(default=False, help_text=_('It is possible to "unlike" a location. Enable this field to hide the least-liked locations'))
  maps_permission     = models.BooleanField(default=False, help_text=_('Give permission to load Google Maps map on location detail page'))

  show_category_label = models.BooleanField(default=True, help_text=_('Show category label on location list page'))
  filter_by_distance  = models.BooleanField(default=False, help_text=_('Allow to filter locations by distance'))
  
  def __str__(self) -> str:
    try:
      return f'Profile of { self.user.get_full_name() if self.user.get_full_name() else self.user.username }'
    except:
      return f'Profile of new user'
  
  def get_absolute_url(self):
      return reverse("location:profile")
  
  def get_home(self):
    return self.home
  
  def name(self):
    try:
      return f"{ _('profile of').capitalize() } { self.user.get_full_name() if self.user.get_full_name() else self.user.username }"
    except:
      return f'Profile of new user'
    
  
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.name = self.name()
    
  def get_favorites(self):
    queryset = Location.objects.filter(favorite_of=self.user.profile)
    family_members = Profile.objects.filter(family=self.user)
    queryset |= Location.objects.filter(favorite_of__in=family_members)
    queryset = queryset.order_by(
        'location__parent__parent', 'location__parent', 'location__name', 'name').distinct()
    return queryset

  def save(self, *args, **kwargs):
    is_new = self.pk is None
    super().save(*args, **kwargs)  # Store object first, to ensure object has a pk

    if is_new:  # if object is new, add default settings
      defaultnavigationapps = NavigationApps.objects.filter(default_enabled=True)
      self.navigationapps.set(defaultnavigationapps)  # Set the default navigation apps

class VisitedIn(VisibilityModel, BaseModel):
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='visits')
  location            = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='visitors')

  MONTHS              = [(1, _('january')), (2, _('february')), (3, _('march')), (4, _('april')), (5, _('may')), (6, _('june')), (7, _('july')), (8, _('august')), (9, _('september')), (10, _('october')), (11, _('november')), (12, _('december'))]
  year                = models.PositiveSmallIntegerField(help_text='')
  month               = models.PositiveSmallIntegerField(blank=True, null=True, help_text='', choices=MONTHS)
  day                 = models.PositiveSmallIntegerField(blank=True, null=True, help_text='', validators=[MinValueValidator(1), MaxValueValidator(31)])
  
  def __str__(self) -> str:
    return f"{ self.user.get_full_name() } visited { self.location.name } in { str(self.year) }"
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # self.slug = self.id

  class Meta:
    ordering = ['location', 'year']
  
  
