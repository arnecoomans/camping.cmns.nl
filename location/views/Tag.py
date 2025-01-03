from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.shortcuts import redirect, reverse
from django.db import IntegrityError

from .snippets.filter_class import FilterClass

from django.db.models import Count

from location.models.Tag import Tag
from location.models.Location import Location

class TagListView(FilterClass, ListView):
  model = Tag

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = _('tags')
    return context

  def get_queryset(self):
    queryset = Tag.objects.all().annotate(childcount=Count('children'))
    queryset = self.filter(queryset)
    queryset = queryset.order_by('parent')
    return queryset

class TagView(FilterClass, DetailView):
  model = Tag

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('tag') }: { self.object.name }"
    children = Tag.objects.filter(parent__slug=self.get_object().slug)
    children = self.filter(children)
    context['children'] = children
    return context

class AddTag(CreateView):
  model = Tag
  fields = ['name', 'parent']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('tags') }: { _('add tag') }"
    ''' Available parent tags used in form
        is filtered to avoid multi-level tags and recursion '''
    context['available_parent_tags'] = Tag.objects.filter(status='p', parent=None)
    return context
  
  def post(self, request, *args, **kwargs):
    ''' Build fields '''
    slug          = slugify(self.request.POST.get('name', ''))
    name          = self.request.POST.get('name', '')
    parent        = None
    list_as       = 'b'
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
  
class EditTag(UpdateView):
  model = Tag
  fields = ['name', 'parent', 'list_as', 'hide_from_filterlist', 'visibility']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('tags') }: { _('add tag') }"
    ''' Available parent tags used in form
        is filtered to avoid multi-level tags and recursion '''
    context['available_parent_tags'] = Tag.objects.filter(status='p', parent=None)
    return context
  
  def form_invalid(self, form):
    messages.add_message(self.request, messages.WARNING, f"{ _('Form cannot be saved because of the following error(s)') }: { form.errors }")
    return super().form_invalid(form)


  def form_valid(self, form):
    if len(form.changed_data) > 0:
      messages.add_message(self.request, messages.SUCCESS, 
                           f"{ _('changes to tag saved') }.")
    else:
      messages.add_message(self.request, messages.INFO,
                           f"{ _('no changes to tag made') }.")
    return super().form_valid(form)
  
class ToggleDeleteTag(UpdateView):
  model = Tag
  fields = ['status']

  def get(self, request, *args, **kwargs):
    ''' Check who can (un)delete tags: staff or superuser ''' 
    if not self.request.user.is_staff or not self.request.user.is_superuser:
      messages.add_message(self.request, messages.ERROR, f"{ _('you are not authorized for this action') }: { _('delete or undelete tag') } \"{ self.get_object().name }\".")
      return redirect('location:tag', self.get_object().slug)
    ''' Check if tag has children '''
    if Tag.objects.filter(parent__slug=self.get_object().slug, status='p').count() > 0:
      messages.add_message(self.request, messages.ERROR, f"{ _('unable to') } { _('delete or undelete tag') } \"{ self.get_object().name }\": { _('Tag has children. Remove children from tag before deleting')}.")
      return redirect('location:tag', self.get_object().slug)
    ''' Change status for tag '''
    new_status = 'x' if self.get_object().status == 'p' else 'p'
    tag = Tag.objects.get(slug=self.get_object().slug)
    tag.status = new_status
    tag.save()
    messages.add_message(self.request, messages.SUCCESS, f"{ _('removed') if new_status == 'x' else _('restored') } { _('tag') } \"{ tag.name }\". <a href=\"{ reverse('location:ToggleDeleteTag', kwargs={'slug': tag.slug}) }\">{ _('Undo') }</a>")
    if tag.parent:
      return redirect('location:tag', self.get_object().parent.slug)
    elif new_status == 'p':
      redirect('location:tag', self.get_object().slug)
    else:
      redirect('location:tags')

class AddTagToLocation(FilterClass, UpdateView):
  model = Location
  template_name = 'location/tag_location_form.html'
  fields = ['tags']
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('tags') }: { _('add tag to') } { self.get_object().name }"
    ''' Available parent tags used in form
        is filtered to avoid multi-level tags and recursion '''
    available_tags = Tag.objects.exclude(locations=self.object).exclude(children__gt=1)
    available_tags = self.filter(available_tags)
    if hasattr(self.request.user, 'profile'):
      ''' Add ignored tags to available tags, to be able to ignore a location based on tags '''
      available_tags = available_tags | self.request.user.profile.ignored_tags.all()
    available_tags = available_tags.order_by('parent__name', 'name')
    context['available_tags'] = available_tags
    return context

  def post(self, request, *args, **kwargs):
    return redirect('location:ToggleTag', self.get_object().slug, self.request.POST.get('object_slug', ''))
    