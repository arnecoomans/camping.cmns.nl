from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from .Location import Location

class Comment(models.Model):
  content             = models.TextField(blank=True, help_text='Markdown is supported')
  location            = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='comments')
  visibility_choices  = (
      ('p', _('public')),
      ('c', _('commmunity')),
      ('f', _('family')),
      ('q', _('private')),
    )
  visibility          = models.CharField(max_length=1, choices=visibility_choices, default='c')

  ''' Record Meta information '''
  status_choices      = (
      ('p', _('published')),
      ('r', _('revoked')),
      ('x', _('deleted')),
    )
  status              = models.CharField(max_length=1, choices=status_choices, default='p')
  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING)

  def __str__(self):
    return f'{ self.user.get_full_name() if self.user.get_full_name() else self.user.username } { _('on') } {self.location.name}'

  def get_absolute_url(self):
    return reverse_lazy('location:location',  kwargs={'slug': self.location.slug }) + '#comments'