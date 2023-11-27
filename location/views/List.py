from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.shortcuts import redirect, reverse
from django.db import IntegrityError, models
from django.conf import settings
from django.http import Http404

from .snippets.filter_class import FilterClass
from .func_filter_visibility import filter_visibility

from location.models.List import List, ListLocation, ListDistance
from location.models.Location import Location
from location.models.Profile import Profile


def addDistance(origin, destination, request):
  distance = ListDistance.objects.get_or_create(origin=origin,
                                                destination=destination,
                                                defaults={
                                                  'user': request.user,
                                                  },
                                                )
  if not distance[0].hasData():
    distance[0].getData(request=request)
    return 1
  return 0

def calculateDistances(request, list):
  queries = 0
  for leg in list.locations.all():
    if leg.getPrevious():
      queries += addDistance(leg.getPrevious().location, leg.location, request)
    if leg.getPreviousLocation():
      queries += addDistance(leg.getPreviousLocation().location, leg.location, request)
    if queries >= settings.MAX_LIST_DISTANCE_QUERIES:
      messages.add_message(request, messages.WARNING, f"{ _('Can calculate a maximum of') } { str(settings.MAX_LIST_DISTANCE_QUERIES) } { _('distances at a time' ) }.")
      return True
    

class ListListView(ListView):
  model = List
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = _('lists')
    return context
  
  def get_queryset(self):
    queryset = List.objects.filter(status='p')
    queryset = filter_visibility(self.request.user, queryset)
    if self.request.GET.get('order_by', '').lower() == 'author':
      queryset = queryset.order_by('user', 'name').distinct()
    elif self.request.GET.get('order_by', '').lower() == 'visibility':
      queryset = queryset.order_by('visibility', 'name').distinct()
    else:
      queryset = queryset.order_by('name').distinct()
    return queryset
  

class ListDetailView(FilterClass, DetailView):
  model = List

  def get_template_names(self):
    if self.get_object().template == 't':
      return ('location/list_trip_detail.html')
    else:
      return ('location/list_list_detail.html')
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('list') }: { self.object.name } { _('by') } { self.object.user }"
    context['locations'] = self.filter(ListLocation.objects.filter(list=self.get_object()))
    return context
  
  def get_object(self):
    try:
      list = List.objects.get(slug=self.kwargs['slug'])
    except List.DoesNotExist:
      messages.add_message(self.request, messages.ERROR,
                           f"{ _('selected list does not exist') }: { self.kwargs['slug'] }.")
      raise Http404(
            _("No list found with the name")
        )
    return list
  
  def get(self, request, *args, **kwargs):
    try:
      return super().get(request, *args, **kwargs)
    except Http404:
      return redirect('location:lists')

class AddList(CreateView):
  model = List
  fields = ['name', 'description', 'visibility', 'template']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('lists') }: { _('add list') }"
    return context
  
  def post(self, request, *args, **kwargs):
    ''' Build fields '''
    slug          = slugify(self.request.POST.get('name', ''))
    name          = self.request.POST.get('name', '')
    description   = self.request.POST.get('description', '')
    visibility    = self.request.POST.get('visibility', '')
    status        = 'p'
    user          = self.request.user
    try:
      list = List.objects.create(
        slug = slug,
        name = name,
        description = description,
        visibility = visibility,
        status = status,
        user = user,
      )
      list.save()
      messages.add_message(self.request, messages.SUCCESS, f"{ _('created list:')} { name }.")
    except IntegrityError as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('list cannot be created') }: { _('a list with this name already exists')} (\"{ name }\").")
      return redirect('location:lists')
    except Exception as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('list cannot be created') }: { e }")
      return redirect('location:lists')
    if 'location' in self.kwargs:
      return redirect('location:AddLocationToList', slug, self.kwargs['location'])
    return redirect('location:list', slug)
  
class EditList(UpdateView):
  model = List
  fields = ['name', 'description', 'visibility', 'template']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('lists') }: { _('edit list') }: { self.object.name }"
    return context
      
  def form_valid(self, form):
    messages.add_message(self.request, messages.SUCCESS, f"List \"{ form.instance.name }\" has been updated.")
    return super().form_valid(form)


''' Edit ListLocation '''
class EditListLocation(FilterClass, UpdateView):
  model = ListLocation
  fields = ['comment', 'visibility', 'nights', 'price', 'media']
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['media'] = self.filter(self.get_object().location.media)
    return context
  
  def get_object(self):
    return ListLocation.objects.get(pk=self.kwargs['pk'], location__slug=self.kwargs['location'])

  def form_invalid(self, form):
    messages.add_message(self.request, messages.WARNING,
                         f"{ _('Form cannot be saved because of the following error(s)') }: { form.errors }")
    return super().form_invalid(form)
  
  def form_valid(self, form):
    if len(form.changed_data) > 0:
      messages.add_message(self.request, messages.SUCCESS, f"{ _('succesfully changed data') }.")
    else:
      messages.add_message(self.request, messages.INFO, f"{ _('no changes made')} ")
    return super().form_valid(form)
  
''' DELETE LIST 
    UNDELETE LIST
    When sharing a message an item has been deleted, it allows for the item to be undeleted. 
'''
class DeleteList(UpdateView):
  model = List
  fields = ['visibility']
      
  def get(self, request, *args, **kwargs):
    list = List.objects.get(slug=self.kwargs['slug'])
    ''' Only allow action from Comment User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      ''' Mark comment as deleted '''
      list.status = 'x'
      list.save()
      messages.add_message(self.request, messages.SUCCESS, f"{ _('List') } \"{ list }\"  { _('has been removed')}. <a href=\"{reverse('location:UndeleteList', args=[list.slug])}\">{ _('Undo') }</a>.")
    else:
      ''' Share errormessage that the comment cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be removed')}. { _('This is not your list') }.")
    ''' Redirect to image, also listing comments '''
    return redirect('location:lists')

class UndeleteList(UpdateView):
  model = List
  fields = ['visibility']
      
  def get(self, request, *args, **kwargs):
    list = List.objects.get(slug=self.kwargs['slug'])
    ''' Only allow action from Comment User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      ''' Mark comment as deleted '''
      list.status = 'p'
      list.save()
      messages.add_message(self.request, messages.SUCCESS, f"{ _('List') } \"{ list }\"  { _('has been restored')} { _('and made visible to') } { list.get_visibility_display() }. <a href=\"{reverse('location:DeleteList', args=[list.slug])}\">{ _('Undo') }</a>.")
    else:
      ''' Share errormessage that the comment cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be restored')}. { _('This is not your list') }.")
    ''' Redirect to list '''
    return redirect('location:list', self.kwargs['slug'])
  

''' ADD LOCATION TO LIST '''
class AddLocationToList(FilterClass, UpdateView):
  model = ListLocation
  fields = ['locations']
  steps = 10

  def get(self, request, *args, **kwargs):
    ''' Should a list be created? '''
    if self.kwargs['slug'] == 'create_new_list':
      return redirect('location:AddListWithLocation', slug=self.kwargs['slug'])
    elif self.request.GET.get('list', '') == 'create_new_list':
      return redirect('location:AddListWithLocation', self.kwargs['slug'])
    elif 'location' in self.kwargs:
      try:
        list = List.objects.get_or_create(slug=self.kwargs['slug'],
                                        defaults={'slug': 'bucketlist_of_' + self.request.user.username,
                                                    'name': 'Bucketlist',
                                                    'visibility': 'f',
                                                    'template': 'l',
                                                    'user': self.request.user})[0]
      except List.DoesNotExist:
        messages.add_message(self.request, messages.ERROR, f"{ _('selected list does not exist') }: { self.kwargs['slug'] }.")
      location = Location.objects.get(slug=self.kwargs['location'])
    elif self.request.GET.get('list', ''):
      try:
        list = List.objects.get_or_create(slug=self.request.GET.get('list', ''),
                                          defaults={'slug': 'bucketlist_of_' + self.request.user.username,
                                                    'name': 'Bucketlist',
                                                    'visibility': 'f',
                                                    'template': 'l',
                                                    'user': self.request.user})[0]
      except List.DoesNotExist:
        messages.add_message(self.request, messages.ERROR,
                             f"{ _('selected list does not exist') }: { self.request.GET.get('list', '') }.")
      location = Location.objects.get(slug=self.kwargs['slug'])
    ''' Add as last item on the list, add self.steps to the last order entry '''
    order = list.getFilteredLocations().last().order + self.steps if list.locations.count() > 0 else self.steps
    ''' If last location is home, move home to last location by setting order one past last '''
    if hasattr(self.request.user, 'profile'):
      if list.getFilteredLocations().count() > 0 and list.getFilteredLocations().last().location == self.request.user.profile.home:
        home = ListLocation.objects.get(id=list.getFilteredLocations().last().id)
        home.order = order + self.steps
        home.save()
        messages.add_message(self.request, messages.INFO, f"{ _('add new location before home') }.")
    ''' Only allow action from Comment User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      ''' Check if location is not most recent location '''
      if list.getFilteredLocations().all().count() > 0:
        if location == list.getFilteredLocations().all().last().location:
          messages.add_message(self.request, messages.ERROR, f"\"{ location.name }\" { _('was not added to list') } { list.name }. { _('This is already the last location on the list') }.")
          return redirect('location:list', list.slug)
      ''' It is safe to store location '''
      listlocation = ListLocation.objects.create(list=list, 
                                                  location=location, 
                                                  order=order,
                                                  user=self.request.user)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Added') } \"{ location.name }\"  { _('to list')} \"{ list.name }\".")
      calculateDistances(self.request, list)
    else:
      ''' Share errormessage that the list cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be modified')}. { _('This is not your list') }.")
    ''' Redirect to list '''
    return redirect('location:list', list.slug)
    
''' Delete Location From List '''
class DeleteLocationFromList(UpdateView):
  model = List
  fields = ['locations']

  def get(self, request, *args, **kwargs):
    list = List.objects.get(slug=self.kwargs['slug'])
    location = list.locations.get(id=self.kwargs['pk'], location__slug=self.kwargs['location'])
    ''' Only allow action from List User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
        if location.status != 'x':
          # location.delete()
          location.status = 'x'
          messages.add_message(self.request, messages.SUCCESS,
                               f"{ _('Removed') } \"{ location.location.name }\"  { _('from list')} \"{ list.name }\". <a href=\"{reverse('location:DeleteLocationFromList', args=[list.slug, location.id, location.location.slug])}\">{ _('Undo') }</a>.")
        else:
          location.status = 'p'
          messages.add_message(self.request, messages.SUCCESS,
                               f"{ _('Restpred') } \"{ location.location.name }\"  { _('to list')} \"{ list.name }\". <a href=\"{reverse('location:DeleteLocationFromList', args=[list.slug, location.id, location.location.slug])}\">{ _('Undo') }</a>.")
        location.save()
    else:
      ''' Share errormessage that the list cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be modified')}. { _('This is not your list') }.")
    ''' Redirect to list '''
    return redirect('location:list', self.kwargs['slug'])
  
''' Add Home '''
class StartListFromHome(UpdateView):
  model = List
  fields = ['location']
  order=0
  def get(self, request, *args, **kwargs):
    list = List.objects.get(slug=self.kwargs['slug'])
    first = list.locations.first().location
    ''' Compare first entry with home of user'''
    ''' Only allow action from List User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      if list.locations.count() == 0 or first != self.request.user.profile.home:
        ListLocation.objects.create(list=list,
                                    location=self.request.user.profile.home,
                                    order=self.order,
                                    user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, f"{ list.name } { _('now departs from')} { self.request.user.profile.home }")
        calculateDistances(self.request, list)
        # messages.add_message(self.request, messages.INFO, f"{ list.name } { _('already departs from')} { self.request.user.profile.home }")
    else:
      ''' Share errormessage that the list cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be modified')}. { _('This is not your list') }.")
    return redirect('location:list', self.kwargs['slug'])

class EndListAtHome(UpdateView):
  model = List
  fields = ['location']
  steps = 10
  def get(self, request, *args, **kwargs):
    list = List.objects.get(slug=self.kwargs['slug'])
    last = list.getFilteredLocations().last().location
    order = list.getFilteredLocations().last().order + self.steps if list.locations.count() > 0 else self.steps
    ''' Compare first entry with home of user'''
    ''' Only allow action from List User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      if list.getFilteredLocations().count() == 0 or last != self.request.user.profile.home:
        ListLocation.objects.create(list=list,
                                    location=self.request.user.profile.home,
                                    order=order,
                                    user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, f"{ list.name } { _('now ends at')} { self.request.user.profile.home }")
        calculateDistances(self.request, list)
      else:
        messages.add_message(self.request, messages.INFO, f"{ list.name } { _('already ends at')} { self.request.user.profile.home }")
    else:
      ''' Share errormessage that the list cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be modified')}. { _('This is not your list') }.")
    return redirect('location:list', self.kwargs['slug'])
  

class ListLocationUpDown(UpdateView):
  model = List
  fields = ['location', 'location__order']

  def get(self, request, direction, *args, **kwargs):
    list = self.get_object()
    location = list.getFilteredLocations().get(pk=self.kwargs['id'], location__slug=self.kwargs['location'])
    ''' Check that location is in list '''
    if location not in list.getFilteredLocations().all():
      messages.add_message(self.request, messages.ERROR, f"{ _('cannot move location') } { location.location.name } { _(direction) }: { _('location is') } { _('not in list') } \"{ list.name }\".")
      return redirect('location:list', self.get_object().slug)
    ''' Get location to change order with '''
    if direction == 'up':
      change_with = location.getPrevious()
    else:
      change_with = location.getNext()
    ''' Check if location is not already first or last'''
    if change_with == None:
      messages.add_message(self.request, messages.ERROR, f"{ _('cannot move location') } { location.location.name } { _(direction) }: { _('location is') } { _('first') if direction == 'up' else _('last') }  { _('in list') } \"{ list.name }\".")
      return redirect('location:list', self.get_object().slug)
    ''' Store ordering '''
    change_with_new_order = location.order
    location.order = change_with.order
    change_with.order = change_with_new_order
    location.save()
    change_with.save()
    messages.add_message(self.request, messages.SUCCESS, f"{ _('moved location') } { location.location.name } { _(direction) } { _('in list') } \"{ list.name }\".")
    ''' See if distances should be calculated '''
    calculateDistances(self.request, list)
    return redirect('location:list', self.get_object().slug)
  
class ListLocationUp(ListLocationUpDown):
  def get(self, request, *args, **kwargs):
    return super().get(request, direction='up', *args, **kwargs)
  
class ListLocationDown(ListLocationUpDown):
  def get(self, request, *args, **kwargs):
    return super().get(request, direction='down', *args, **kwargs)

class AutomatedFavoriteList(FilterClass, ListView):
  model = Location
  template_name = 'location/list_favorite_detail.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = _('favorites')
    media = {}
    for location in self.get_queryset():
      if self.filter(location.media).count() > 0:
        media[location.id] = self.filter(location.media).first()
    context['media'] = media
    return context


  def get_queryset(self):
    ''' Fetch Logged In User Favorites '''
    queryset = Location.objects.none()
    if hasattr(self.request.user, 'profile'):
      return self.filter(self.request.user.profile.get_favorites())
      queryset = self.filter_favorites(Location.objects.all())
    family_members = Profile.objects.filter(family=self.request.user)
    queryset = Location.objects.filter(favorite_of__in=family_members)
    queryset = self.filter(queryset).order_by(
        'location__parent__parent', 'location__parent', 'location__name', 'name').distinct()
    return queryset