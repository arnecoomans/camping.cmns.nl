from django.db import models
from .base_model import BaseModel

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
