from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
  ''' Base Model
      Holds fields that are common in most models, and that are 
      maintained centrally.
  '''
  ''' Record Meta information '''
  visibility_choices      = (
      ('p', _('public')),
      ('c', _('commmunity')),
      ('f', _('family')),
      ('q', _('private')),
    )
  visibility          = models.CharField(max_length=1, choices=visibility_choices, default='c')
  
  status_choices      = (
      ('p', _('published')),
      ('r', _('revoked')),
      ('x', _('deleted')),
    )
  status              = models.CharField(max_length=1, choices=status_choices, default='p')
  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING)

  class Meta:
    abstract = True