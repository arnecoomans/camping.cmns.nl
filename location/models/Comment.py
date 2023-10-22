from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from .base_model import BaseModel
from .Location import Location

class Comment(BaseModel):
  content             = models.TextField(blank=True, help_text='Markdown is supported')
  location            = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='comments')

  def __str__(self):
    return f"{ self.user.get_full_name() if self.user.get_full_name() else self.user.username } { _('on') } {self.location.name}"

  def get_absolute_url(self):
    return reverse_lazy('location:location',  kwargs={'slug': self.location.slug }) + '#comments'