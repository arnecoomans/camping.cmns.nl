
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.template.loader import render_to_string

import markdown


from ..snippets.filter_class import FilterClass

from location.models.Comment import Comment
from location.models.Location import Location


# class BaseClass:
#   def getDefaultData(self):
#     return {
#       'error': False,
#       'message': '',
#       'payload': '',
#     }

# class aListComments(BaseClass, FilterClass, ListView):
#   model = Comment

#   def get(self, request, *args, **kwargs):
#     ''' Validate that user is logged in '''
#     if self.verifyUserAuthenticated() is not True and not settings.ALLOW_UNAUTHENTICATED_READ_COMMENTS:
#       return self.verifyUserAuthenticated()
#     ''' Validate location '''
#     location = self.getLocation()
#     if not location:
#       return self.getLocationError()
#     ''' Proceed processing request '''
#     response = self.getDefaultData()
#     comments = Comment.objects.all()
#     ''' Process Filters '''
#     if location:
#       comments = comments.filter(location=location)
#     if self.request.GET.get('user', False):
#       comments = comments.filter(user=self.request.GET.get('user'))
#     response['data']['comments'] = []
#     ''' Filter comments by status and visibility '''
#     comments = self.filter(comments).order_by('-date_modified').distinct()
#     # ''' Add comments to response '''
#     # for comment in comments:
#     #   response['data']['comments'].append({
#     #     'id': comment.id,
#     #     'location': { 
#     #       'slug': comment.location.slug,
#     #       'name': comment.location.name,
#     #       'id': comment.location.id,
#     #     },
#     #     'content': md.convert(strip_tags(comment.content)),
#     #     'user': { 
#     #       'id': comment.user.id,
#     #       'username': comment.user.username,
#     #       'displayname': comment.user.get_full_name() if comment.user.get_full_name() else comment.user.username,
#     #     },
#     #     'date_added': comment.date_added,
#     #     'visibility': comment.get_visibility_display(),
#     #   })
#     ''' Add rendered comments to payload '''
#     response['payload'] = []
#     for comment in comments:
#       response['payload'].append(render_to_string('partial/comment.html', {'comment': comment, 'user': self.request.user}))
#     return JsonResponse(response)

class aAddComment(CreateView):
  model = Comment
  fields = ['location', 'visibility', 'content']

  def get(self, request, *args, **kwargs):
    message = ''
    status = 200
    ''' Check if user is allowed to comment '''
    if not self.request.user.is_authenticated:
      status = 403
      message = _('you need to be logged in to comment').capitalize()
    else:
      ''' Verify Location '''
      try:
        location = Location.objects.get(slug=self.kwargs['location'])
      except KeyError:
        status = 500
        message = _('no valid location slug provided').capitalize()
      except Location.DoesNotExist:
        status = 404
        message = _('location not found').capitalize()
    if status != 200:
      return JsonResponse({'status': status, 'message': message})
    ''' Retrieve Visibility '''
    if 'visibility' in self.request.GET:
      visibility = self.request.GET.get('visibility', 'p')
    elif 'visibility' in self.request.POST:
      visibility = self.request.POST.get('visibility', 'p')
    else:
      visibility = 'p'
    ''' Retrieve Comment '''
    if 'comment' in self.request.GET:
      comment = self.request.GET.get('comment', '')
    elif 'comment' in self.request.POST:
      comment = self.request.POST.get('comment', '')
    else:
      comment = ''
    if len(comment) < 5:
      status = 400
      message = _('comment too short').capitalize() + ': ' + str(comment)
    comment = {
      'location': location,
      'visibility': visibility,
      'content': comment,
      'user': self.request.user,
    }
    ''' Check if Comment already exists '''
    if Comment.objects.filter(location=location, user=self.request.user, content=comment['content']).exists():
      status = 409
      message = _('you already commented this').capitalize()
    if status == 200:
      ''' Create Comment '''
      comment = Comment.objects.create(**comment)
      message = _('comment added').capitalize()
    ''' Build Success URL '''
    success_url = reverse('location:getAttributesFor', kwargs={'location': location.slug, 'attribute': 'comment'})
    return JsonResponse({'message': str(message), 'success-url': success_url}, status=status)

    

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