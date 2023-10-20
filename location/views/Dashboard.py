from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.db.models import Count

from location.models.Location import Location
from location.models.Comment import Comment
from location.models.List import List
from location.models.Tag import Tag

class DashboardView(TemplateView):
  template_name = 'location/dashboard.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['recent_locations']   = self.get_recent_locations()
    context['recent_comments']    = self.get_recent_comments()
    context['recent_lists']       = self.get_recent_lists()
    context['popular_tags']       = self.get_popular_tags()
    return context  
  
  def get_recent_locations(self):
    locations = Location.objects.filter(status='p')
    locations = self.filter_visibility(locations)
    locations = locations.order_by('-date_modified')[:5]
    return locations

  def get_recent_comments(self):
    comments = Comment.objects.filter(status="p")
    comments = self.filter_visibility(comments)
    comments = comments.order_by('-date_modified')[:5]
    return comments
  
  def get_recent_lists(self):
    lists = List.objects.filter(status='p')
    lists = self.filter_visibility(lists)
    lists = lists.order_by('-date_modified')[:5]
    return lists
  
  def get_popular_tags(self):
    tags = Tag.objects.filter(status='p').annotate(count=Count('locations')).filter(count__gt=0).order_by('-count')[:5]
    return tags
  
  def filter_visibility(self, queryset):
    ''' Add private objects for current user to queryset '''
    if self.request.user.is_authenticated:
      ''' Process visibility filters '''
      queryset =  queryset.filter(visibility='p') |\
                  queryset.filter(visibility='c') |\
                  queryset.filter(visibility='f', user=self.request.user) |\
                  queryset.filter(visibility='f', user__profile__family=self.request.user) |\
                  queryset.filter(visibility='q', user=self.request.user)
    else:
      queryset =  queryset.filter(visibility='p')
    return queryset