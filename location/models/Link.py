from django.db import models
from django.utils.translation import gettext_lazy as _

from cmnsd.models.cmnsd_basemodel import BaseModel, VisibilityModel

from urllib.parse import urlparse

''' Links model
    Any location may have multiple links related to the location, such as several review websites
'''
class Link(VisibilityModel,BaseModel):
  name                = models.CharField(max_length=255, blank=True, help_text=_('Title of link, optional'))
  url                 = models.CharField(max_length=512, unique=True, help_text=_('full url of link'))
  primary             = models.BooleanField(default=False, help_text=_('primary link for location'))  

  def __str__(self) -> str:
    return self.get_title()

  def get_title(self):
    if self.name:
      return self.name
    hostname = self.hostname()
    if 'google' in hostname:
      ''' Google Maps results 
          Return the search query as title
          Search query is the string after /maps/search/
      '''
      if 'maps/' in self.url:
        query = self.url.split('/')
        counter = 0
        for q in query:
          if 'search' in q:
            query = query[counter+1].replace('+', ' ').capitalize()
            break
          counter += 1
        query = query if len(query) > 0 else _('search')
        return f"{ query } on { hostname.capitalize() } Maps"
      ''' Google search results 
          Return the search query as title
          Search query is the string after ?q=    
      '''
      query = urlparse(self.url).query
      query = query.split('&')
      for q in query:
        if 'q=' in q:
          query = q.replace('q=', '')
          break
      query = query if str(query) != "['']" else _('search').capitalize()
      return f"{ query } on { hostname.capitalize() }"
    return hostname
  
  def save(self, *args, **kwargs):
    ''' Enforce URL to be correct '''
    if not self.url.startswith('http://') and not self.url.startswith('https://'):
      self.url = f"https://{ self.url }"
    return super(Link, self).save(*args, **kwargs)
    
  def hostname(self):
    if urlparse(self.url).hostname:
      return urlparse(self.url).hostname.replace('www.', '')
    elif self.url:
      return self.url
    return _('no url')
  
  class Meta:
        ordering = ['-primary', 'url']