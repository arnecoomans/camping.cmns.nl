from django.forms.models import BaseModelForm
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.shortcuts import redirect
from django.db import IntegrityError

from django.db.models import Count


from location.models.Tag import Tag

class TagListView(ListView):
  model = Tag

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = _('tags')
    return context

  def get_queryset(self):
    queryset = Tag.objects.all().annotate(childcount=Count('children')).order_by('parent')
    return queryset

class TagView(DetailView):
  model = Tag

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('tag') }: { self.object.name }"
    return context

class AddTag(CreateView):
  model = Tag
  fields = ['name', 'parent']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('tags') }: { _('add tag') }"
    ''' Available parent tags used in form
        is filtered to avoid multi-level tags and recursion '''
    context['available_parent_tags'] = Tag.objects.filter(parent=None)
    return context

  
  def post(self, request, *args, **kwargs):
    ''' Build fields '''
    slug          = slugify(self.request.POST.get('name', ''))
    name          = self.request.POST.get('name', '')
    parent        = None
    list_as       = 'b'
    status        = 'p'
    user          = self.request.user
    ''' Check if parent tag should be used '''
    if self.request.POST.get('parent', '') and self.request.POST.get('parent', '') != '-'*len(self.request.POST.get('parent', '')):
      parent = Tag.objects.get(pk=self.request.POST.get('parent', ''))
    ''' Avoid Specific Tags '''
    if name[:8] == '-'*8 or name.lower() == 'create_new':
      messages.add_message(self.request, messages.ERROR, f"{ _('protected tag') } { name } { _('cannot be used')}.")
      return redirect('location:tags')
    ''' Store Tag '''
    try:
      tag = Tag.objects.create(
        slug = slug,
        name = name,
        parent = parent,
        list_as = list_as,
        status = status,
        user = user,
      )
      tag.save()
      messages.add_message(self.request, messages.SUCCESS, f"{ _('created tag:')} { name }.")
    except IntegrityError as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('tag cannot be created') }: { _('a tag with this name already exists')} (\"{ name }\").")
      return redirect('location:tag', slug)
    except Exception as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('tag cannot be created') }: { e }")
      return redirect('location:tags')
    ''' Redirect to Add Tag To Location if location slug is in request url '''
    if 'slug' in self.kwargs:
      return redirect('location:ToggleTag', self.kwargs['slug'], slug)
    return redirect('location:tag', slug)
  