from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.db import IntegrityError
from django.conf import settings

from .func_filter_visibility import filter_visibility

from django.contrib.auth.models import User

from location.models.Location import Location, Category, Chain
from location.models.Profile import Profile
from location.models.Comment import Comment
from location.models.Tag import Tag
from location.models.List import List, ListLocation
from location.models.Profile import VisitedIn

''' TOGGLE View
    The ToggleView holds some basic functionaliy that is used in all Toggle functions.
    This mainly fetches the toggled objects identifier from the url

    The ToggleView extends an object view that requires:
    - set a Model where the Object is Toggled
    - function handle_exception 
    - class toggle that does the actual toggling.
'''
class ToggleView(UpdateView):
  def get_success_url(self) -> str:
    return reverse_lazy('location:EditLocation', kwargs={'slug': self.get_object().slug})
  
  def get(self, request, *args, **kwargs):
    if 'object_slug' in kwargs:
      object_slug = kwargs['object_slug']
    elif self.request.GET.get('object_slug', ''):
      object_slug = self.request.GET.get('object_slug', '')
    else:
      messages.add_message(self.request, messages.ERROR(f"{ _('no searchable object passed in URL') }."))
    if object_slug in ['--------', 'create_new']:
      return self.handle_exceptions(object_slug)
    self.toggle(object_slug)
    return redirect(self.get_success_url())
  
  def post(self, request, *args, **kwargs):
    object_slug = request.POST.get('object_slug')
    # messages.add_message(self.request, messages.INFO, object_slug)
    if object_slug in ['--------', 'create_new']:
      return self.handle_exceptions(object_slug)
    self.toggle(object_slug)
    return redirect(self.get_success_url())


''' LOCATION '''
''' Toggle Chain '''
class ToggleChain(ToggleView):
  model = Location
  fields = ['chain']

  def handle_exceptions(self, object_slug):
    if object_slug[:8] == '-'*8:
      messages.add_message(self.request, messages.ERROR, f"{ _('no chain selected from dropdown list') }.")
      return redirect(self.get_success_url())
    elif object_slug == 'create_new':
      messages.add_message(self.request, messages.INFO, f"{ _('new chain will be added to') } { self.get_object().name }.")
      return redirect('location:AddChainTo', self.get_object().slug)
    return True

  def toggle(self, object_slug):
    try:
      object = Chain.objects.get(slug=object_slug)
    except Chain.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('can not find chain with slug ')} { object_slug }")
      return redirect(self.get_success_url())
    if object == self.get_object().chain:
      ''' Chain should be removed '''
      object.locations.remove(self.get_object())
      messages.add_message(self.request, messages.SUCCESS, f"{ _('removed') } { _('chain') } { object.name } { _('from') } { self.get_object().name }")
    else:
      ''' Chain should be added '''
      object.locations.add(self.get_object())
      messages.add_message(self.request, messages.SUCCESS, f"{ _('added') } { _('chain') } { object.name } { _('to') } { self.get_object().name }")
    self.get_object().save()


''' Toggle Category '''
class ToggleCategory(ToggleView):
  model = Location
  fields = ['additional_category']

  def get_success_url(self) -> str:
    return reverse_lazy('location:EditLocation', kwargs={'slug': self.get_object().slug})
  
  def handle_exceptions(self, object_slug):
    if object_slug[:8] == '-'*8:
      messages.add_message(self.request, messages.ERROR, f"{ _('no category selected from dropdown list') }.")
      return redirect(self.get_success_url())
    return True

  def toggle(self, object_slug):
    ''' Find Category '''
    try:
      object = Category.objects.get(slug=object_slug)
    except Category.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('can not find category with slug ')} { object_slug }")
      return redirect(self.get_success_url())
    ''' Toggle '''
    if object in self.get_object().additional_category.all():
      ''' Tag should be removed '''
      self.get_object().additional_category.remove(object)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('removed') } { _('category') } { object.name } { _('from') } { self.get_object().name }")
    else:
      ''' Tag should be added '''
      self.get_object().additional_category.add(object)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('added') } { _('category') } { object.name } { _('to') } { self.get_object().name }")
  
''' Toggle Tag '''
class ToggleTag(ToggleView):
  model = Location
  fields = ['tags']

  def get_success_url(self) -> str:
    return reverse_lazy('location:EditLocation', kwargs={'slug': self.get_object().slug})
  
  def handle_exceptions(self, object_slug):
    if object_slug[:8] == '-'*8:
      messages.add_message(self.request, messages.ERROR, f"{ _('no tag selected from dropdown list') }.")
      return redirect(self.get_success_url())
    elif object_slug == 'create_new':
      messages.add_message(self.request, messages.INFO, f"{ _('new tag will be added to') } { self.get_object().name }.")
      return redirect('location:AddTagTo', self.get_object().slug)
    return True

  def toggle(self, object_slug):
    ''' Find Tag '''
    try:
      object = Tag.objects.get(slug=object_slug)
    except Tag.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('can not find tag with slug ')} { object_slug }")
      return redirect(self.get_success_url())
    ''' Toggle '''
    if object in self.get_object().tags.all():
      ''' Tag should be removed '''
      self.get_object().tags.remove(object)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('removed') } { _('tag') } { object.name } { _('from') } { self.get_object().name }")
    else:
      ''' Tag should be added '''
      self.get_object().tags.add(object)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('added') } { _('tag') } { object.name } { _('to') } { self.get_object().name }")
  
''' PROFILE '''
''' Toggle Favorite '''
class ToggleFavorite(UpdateView):
  model = Location
  fields = ['favorite_of']

  def get(self, request, *args, **kwargs):
    location = Location.objects.get(slug=kwargs['slug'])
    ''' Verify that the user has a profile. If not, create a profile '''
    if hasattr(self.request.user, 'profile'):
      profile = self.request.user.profile
    else:
      profile = Profile.objects.create(user=self.request.user)
      messages.add_message(self.request, messages.INFO, f"Created profile for { self.request.user.get_full_name() }")
    ''' If Location is in Favorites, remove it '''
    if location in profile.favorite.all():
      profile.favorite.remove(location)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Removed') } { location } { _('from favorites') }.")
    else:
      profile.favorite.add(location)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Added') } { location } { _('to favorites') }.")
    return redirect('location:location', location.slug)

''' Toggle Least-liked '''
class ToggleLeastLiked(UpdateView):
  model = Location
  fields = ['least_liked_of']

  def get(self, request, *args, **kwargs):
    location = Location.objects.get(slug=kwargs['slug'])
    ''' Verify that the user has a profile. If not, create a profile '''
    if hasattr(self.request.user, 'profile'):
      profile = self.request.user.profile
    else:
      profile = Profile.objects.create(user=self.request.user)
      messages.add_message(self.request, messages.INFO, f"Created profile for { self.request.user.get_full_name() }")
    ''' If Location is in Favorites, remove it '''
    if location in profile.least_liked.all():
      profile.least_liked.remove(location)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Removed') } { location } { _('from least-liked') }.")
    else:
      profile.least_liked.add(location)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Added') } { location } { _('to least-liked') }.")
    return redirect('location:location', location.slug)
  

''' Toggle Family Member '''
class ToggleFamilyMember(UpdateView):
  model = User
  fields = ['id']

  def get(self, request, *args, **kwargs):
    family_member = User.objects.get(id=kwargs['id'])
    if hasattr(self.request.user, 'profile'):
      profile = self.request.user.profile
    else:
      profile = Profile.objects.create(user=self.request.user)
      messages.add_message(self.request, messages.INFO, f"Created profile for { self.request.user.get_full_name() }")
    ''' If User is already a family member '''
    if family_member in profile.family.all():
      profile.family.remove(family_member)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Removed') } { family_member.get_full_name() } { _('from family') }.")
    else:
      profile.family.add(family_member)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Added') } { family_member.get_full_name() } { _('to family') }.")
    return redirect('location:profile')