
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings

from .func_filter_status import filter_status
from .func_filter_visibility import filter_visibility

from location.models.Comment import Comment

class AddComment(CreateView):
  model = Comment
  fields = ['location', 'visibility', 'content']

  def form_valid(self, form):
    ''' Force comment user to be logged in user '''
    form.instance.status = 'p'
    form.instance.user = self.request.user
    messages.add_message(self.request, messages.SUCCESS, f"{ _('Comment added to') } \"{form.instance.location.name}\"")
    return super().form_valid(form)
  
class EditComment(UpdateView):
  model = Comment
  fields = ['location', 'visibility', 'content']

class CommentListView(ListView):
  model = Comment
  paginate_by = settings.PAGINATE

  def get_queryset(self):
    queryset = Comment.objects.all()
    queryset = filter_status(self.request.user, queryset)
    queryset = filter_visibility(self.request.user, queryset)
    queryset = queryset.order_by('-date_modified').distinct()

    return queryset

class CommentByUserListView(ListView):
  model = Comment
  paginate_by = settings.PAGINATE

  def get_queryset(self):
    try:
      user = User.objects.get(username=self.kwargs['username'])
    except User.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('can not find user') } { _('to list comments of') }.")
      return Comment.objects.none()
    queryset = Comment.objects.filter(user=user)
    queryset = filter_status(self.request.user, queryset)
    queryset = filter_visibility(self.request.user, queryset)
    queryset = queryset.order_by('-date_modified').distinct()
    return queryset


class DeleteComment(UpdateView):
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
  
class UndeleteComment(UpdateView):
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