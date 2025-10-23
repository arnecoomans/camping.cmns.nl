
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings

from .snippets.filter_class import FilterClass

from location.models.Comment import Comment
from location.models.Location import Location

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

class CommentListView(FilterClass, ListView):
  model = Comment
  # paginate_by = settings.PAGINATE

  def get_queryset(self):
    queryset = Comment.objects.all()
    locations = Location.objects.all()
    locations = self.filter(locations)
    queryset = self.filter(queryset)
    queryset = queryset.filter(location__in=locations.values_list('id', flat=True))
    queryset = queryset.order_by('-date_modified').distinct()
    return queryset

class CommentByUserListView(FilterClass, ListView):
  model = Comment
  # paginate_by = settings.PAGINATE

  def get_queryset(self):
    try:
      user = User.objects.get(username=self.kwargs['username'])
    except User.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('can not find user') } { _('to list comments of') }.")
      return Comment.objects.none()
    queryset = Comment.objects.filter(user=user)
    locations = Location.objects.all()
    locations = self.filter(locations)
    queryset = self.filter(queryset)
    queryset = queryset.filter(location__in=locations.values_list('id', flat=True))
    queryset = self.filter(queryset)
    queryset = queryset.order_by('-date_modified').distinct()
    return queryset