from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .Location import Location

class Profile(models.Model):
  user                = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='profile', unique=True)

  home                = models.ForeignKey(Location, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='home_of')
  family              = models.ManyToManyField(User, blank=True, help_text=_('family members'), related_name='famlily_of')

  favorite            = models.ManyToManyField(Location, blank=True, related_name='favorite_of')
  least_liked         = models.ManyToManyField(Location, blank=True, related_name='least_liked_of')

  def __str__(self) -> str:
    return f'Profile of { self.user.get_full_name() if self.user.get_full_name() else self.user.username }'
  
  def get_absolute_url(self):
      return reverse("location:profile")
  
  def get_home(self):
    return self.home
  
class VisitedIn(BaseModel):
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='visits')
  location            = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='visitors')

  MONTHS              = [(1, _('january')), (2, _('february')), (3, _('march')), (4, _('april')), (5, _('may')), (6, _('june')), (7, _('july')), (8, _('august')), (9, _('september')), (10, _('october')), (11, _('november')), (12, _('december'))]
  year                = models.PositiveSmallIntegerField(help_text='')
  month               = models.PositiveSmallIntegerField(blank=True, null=True, help_text='', choices=MONTHS)
  day                 = models.PositiveSmallIntegerField(blank=True, null=True, help_text='', validators=[MinValueValidator(1), MaxValueValidator(31)])
  
  def __str__(self) -> str:
    return f"{ self.user.get_full_name() } visited { self.location.name } in { str(self.year) }"
  
  class Meta:
    ordering = ['year']