from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.conf import settings
from django.utils.translation import gettext_lazy as _

''' Category model
'''
class Category(models.Model):
  slug                = models.CharField(max_length=255, unique=True, help_text=f"{ _('Identifier in URL') } ({ _('automatically generated') })")
  name                = models.CharField(max_length=255, help_text=_('Name of category'))
  parent              = models.ForeignKey("self", on_delete=models.CASCADE, related_name='children', null=True, blank=True)
  
  ''' Record Meta information '''
  date_added          = models.DateTimeField(editable=False, auto_now_add=True)
  date_modified       = models.DateTimeField(editable=False, auto_now=True)
  user                = models.ForeignKey(User, on_delete=models.DO_NOTHING)

  class Meta:
    verbose_name_plural = 'categories'
    ordering = ['parent__name', 'name']

  def __str__(self) -> str:
    if self.parent:
      return f"{ self.parent.name }: { self.name }"
    return self.name
  
  def get_absolute_url(self):
    return reverse_lazy('location:locations') + f"?category={ self.slug }"
  
  js_template_name = 'categories'