from django.views.generic.edit import CreateView
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.urls import reverse
from django.shortcuts import redirect
from django.db import IntegrityError

from location.models.Location import Chain

class AddChain(CreateView):
  model = Chain
  fields = ['name', 'parent', 'description', 'website']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('chain') }: { _('add chain') }"
    return context

  def post(self, request, *args, **kwargs):
    ''' Build fields '''
    slug          = slugify(self.request.POST.get('name', ''))
    name          = self.request.POST.get('name', '')
    parent        = None
    website       = 'https://google.com/?q=' + self.request.POST.get('name', '')
    description   = 'foo'
    user          = self.request.user
    if self.request.POST.get('website', '') != '':
      website = self.request.POST.get('website', '')
    ''' Check if parent tag should be used '''
    if self.request.POST.get('parent', ''):
      parent = Chain.objects.get(pk=self.request.POST.get('parent', ''))
    ''' Store Tag '''
    try:
      chain = Chain.objects.create(
        slug = slug,
        name = name,
        parent = parent,
        website = website,
        description = description,
        user = user,
      )
      chain.save()
      messages.add_message(self.request, messages.SUCCESS, f"{ _('created chain:')} { name }.")
    except IntegrityError as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('chain cannot be created') }: { _('a chain with this name already exists')} (\"{ name }\"). { e }")
      return redirect(reverse('location:locations') + '?chain=' + slug)
    except Exception as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('chain cannot be created') }: { e }")
      return redirect('location:locations')
    ''' Redirect to Add Tag To Location if location slug is in request url '''
    if 'slug' in self.kwargs:
      return redirect('location:ToggleChain', self.kwargs['slug'], slug)
    return redirect('location:locations')
  