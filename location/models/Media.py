from django.db import models
from .base_model import BaseModel
from django.conf import settings
from .Location import Location


class Media(BaseModel):
  source = models.ImageField()
  title = models.CharField(max_length=255)

  location = models.ForeignKey(
      Location, on_delete=models.DO_NOTHING, null=True, blank=True)

  def __str__(self) -> str:
    return f"{ self.title } ({ self.location.name })"

  class Meta:
    verbose_name_plural = 'media'
    ordering = ['visibility', 'date_modified']
  
  def save(self, *args, **kwargs):
    ''' If no title is given, use source file name as title '''
    if not self.title:
      self.title = str(self.source.name.replace('_', ' '))
    ''' Convert HEIC to JPG '''
    
    return super(Media, self).save(*args, **kwargs)
    
