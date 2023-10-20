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
