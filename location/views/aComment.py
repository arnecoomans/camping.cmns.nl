
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

class aAddComment(aHelper, CreateView):
  model = Comment
  fields = ['location', 'visibility', 'content']

  def get(self, request, *args, **kwargs):
    ''' Validate that user is logged in '''
    if self.verifyUserAuthenticated() is not True:
      return self.verifyUserAuthenticated()
    ''' Validate location '''
    location = self.getLocation()
    if not location:
      return self.getLocationError()
    ''' Validate comment '''
    comment = self.request.GET.get('comment', False)
    if not comment:
      return self.getInputError('comment')
    ''' Validate visibility '''
    visibility = self.request.GET.get('visibility', 'c')
    if visibility not in ['p', 'c', 'f', 'q']:
      return self.getInputError('visibility')
    ''' Proceed processing request '''
    response = self.getDefaultData()
    result = Comment.objects.create(location=location, user=self.request.user, content=comment, visibility=visibility)
    response['data']['comment'] = {
      'id': result.id,
      'content': result.content,
      'user': result.user.username,
      'date_added': result.date_added,
      'visibility': result.visibility,
    }
    return JsonResponse(response)
  

class aEditComment(UpdateView):
  model = Comment
  fields = ['location', 'visibility', 'content']

class aCommentListView(FilterClass, ListView):
  model = Comment
  paginate_by = settings.PAGINATE

  def get_queryset(self):
    queryset = Comment.objects.all()
    queryset = self.filter(queryset)
    queryset = queryset.order_by('-date_modified').distinct()

    return queryset

class aCommentByUserListView(FilterClass, ListView):
  model = Comment
  paginate_by = settings.PAGINATE

  def get_queryset(self):
    try:
      user = User.objects.get(username=self.kwargs['username'])
    except User.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('can not find user') } { _('to list comments of') }.")
      return Comment.objects.none()
    queryset = Comment.objects.filter(user=user)
    queryset = self.filter(queryset)
    queryset = queryset.order_by('-date_modified').distinct()
    return queryset


class aDeleteComment(UpdateView):
  model = Comment
  fields = ['status']

  def get(self, request, *args, **kwargs):
    comment = Comment.objects.get(pk=self.kwargs['pk'])
    ''' Only allow action from Comment User or Staff'''
    if comment.user == self.request.user or self.request.user.is_superuser():
      ''' Mark comment as deleted '''
      comment.status = 'x'
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Comment') } \"{ comment }\"  { _('has been removed')}. <a href=\"{reverse('location:UndeleteComment', args=[comment.id])}\">{ _('Undo') }</a>.")
    else:
      ''' Share errormessage that the comment cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('Comment') } \"{ comment }\" { _('cannot be removed')}. { _('This is not your comment')}")
    comment.save()
    ''' Redirect to image, also listing comments '''
    return redirect('location:location', comment.location.slug)
  
class aUndeleteComment(UpdateView):
  model = Comment
  fields = ['status']

  def get(self, request, *args, **kwargs):
    comment = Comment.objects.get(pk=self.kwargs['pk'])
    ''' Only allow action from Comment User or Staff'''
    if comment.user == self.request.user or self.request.user.is_superuser():
      ''' Mark comment as deleted '''
      comment.status = 'p'
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Comment') } \"{ comment }\"  { _('has been restored')}. <a href=\"{reverse('location:DeleteComment', args=[comment.id])}\">{ _('Undo') }</a>.")
    else:
      ''' Share errormessage that the comment cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('Comment') } \"{ comment }\" { _('cannot be removed')}. { _('This is not your comment')}")
    comment.save()
    ''' Redirect to image, also listing comments '''
    return redirect('location:location', comment.location.slug)