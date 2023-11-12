from typing import Any
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.shortcuts import redirect, reverse
from django.db import IntegrityError
from django.conf import settings

from pathlib import Path

from location.models.Media import Media
from location.models.Location import Location

class AddMediaToLocation(CreateView):
  model = Media
  fields = ['source', 'title', 'location', 'visibility']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('media') }: { _('add media') }"
    context['location'] = Location.objects.get(slug=self.kwargs['slug'])
    return context
  
  def form_invalid(self, form):
    messages.add_message(self.request, messages.WARNING, f"{ form.cleaned_data }")
    messages.add_message(self.request, messages.WARNING, f"{ _('Form cannot be saved because of the following error(s)') }: { form.errors }")
    return super().form_invalid(form)

  def get_initial(self):
    initial = super().get_initial()
    # try:
    #   initial['location'] = Location.objects.get(slug=self.kwargs['slug'])
    # except Location.DoesNotExist:
    #   messages.add_message(self.request, messages.ERROR, f"_('unknown location to add media to')")

    return initial
  
  def form_valid(self, form):
    ''' Force user '''
    if not hasattr(form.instance, 'user'):
      form.instance.user = self.request.user
    if not form.instance.title:
      form.instance.title = Path(self.request.FILES['source'].name).stem.replace('_', ' ')
    messages.add_message(self.request, messages.SUCCESS, f"{ _('succesfully added image to location') } { form.instance.location.name }.")
    return super().form_valid(form)
  
  def get_success_url(self) -> str:
    return reverse('location:location', kwargs={'slug': self.kwargs['slug']})