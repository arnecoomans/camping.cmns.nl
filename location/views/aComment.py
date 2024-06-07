
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse

from .snippets.a_helper import aHelper
from .snippets.filter_class import FilterClass

from location.models.Comment import Comment


class aListComments(aHelper, FilterClass, ListView):
  model = Comment

  def get(self, request, *args, **kwargs):
    ''' Validate that user is logged in '''
    if self.verifyUserAuthenticated() is not True:
      return self.verifyUserAuthenticated()
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Proceed processing request '''
    response = self.getDefaultData()
    comments = Comment.objects.all()
    ''' Process Filters '''
    if location:
      comments = comments.filter(location=location)
    if self.request.GET.get('user', False):
      comments = comments.filter(user=self.request.GET.get('user'))
    response['data']['comments'] = []
    ''' Filter comments by status and visibility '''
    comments = self.filter(comments).order_by('-date_modified').distinct()
    ''' Add comments to response '''
    for comment in comments:
      response['data']['comments'].append({
        'id': comment.id,
        'location': { 
          'slug': comment.location.slug,
          'name': comment.location.name,
          'id': comment.location.id,
        },
        'content': comment.content,
        'user': { 
          'id': comment.user.id,
          'username': comment.user.username,
          'displayname': comment.user.get_full_name(),
        },
        'date_added': comment.date_added,
        'visibility': comment.get_visibility_display(),
      })
    return JsonResponse(response)
