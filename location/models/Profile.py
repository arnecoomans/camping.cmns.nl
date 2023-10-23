from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse

from django.utils.translation import gettext_lazy as _

from .Location import Location

class Profile(models.Model):
  user                = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='profile', unique=True)

  home                = models.ForeignKey(Location, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='home_of')
  family              = models.ManyToManyField(User, blank=True, help_text=_('family members'), related_name='famlily_of')

  favorite            = models.ManyToManyField(Location, blank=True, related_name='favorite_of')
  def __str__(self) -> str:
    return f'Profile of { self.user.get_full_name() if self.user.get_full_name() else self.user.username }'
  
  def get_absolute_url(self):
      return reverse("location:profile")
  
  def get_home(self):
    return self.home