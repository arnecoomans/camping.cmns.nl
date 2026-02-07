from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

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
  