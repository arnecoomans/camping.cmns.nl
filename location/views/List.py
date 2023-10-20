from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.shortcuts import redirect, reverse
from django.db import IntegrityError


from location.models.List import List, ListLocation, ListDistance
from location.models.Location import Location


class ListListView(ListView):
  model = List
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = _('lists')
    return context
  
  def get_queryset(self):
    queryset = List.objects.filter(status='p')
    if self.request.user.is_authenticated:
      queryset =  queryset.filter(visibility='p') |\
                  queryset.filter(visibility='c') |\
                  queryset.filter(visibility='f', user__profile__family=self.request.user) |\
                  queryset.filter(visibility='f', user=self.request.user) |\
                  queryset.filter(visibility='q', user=self.request.user)
    else:
      queryset = queryset.filter(visibility='p')
    if self.request.GET.get('order_by', '').lower() == 'author':
      queryset = queryset.order_by('user', 'name').distinct()
    elif self.request.GET.get('order_by', '').lower() == 'visibility':
      queryset = queryset.order_by('visibility', 'name').distinct()
    else:
      queryset = queryset.order_by('name').distinct()
    return queryset
  

class ListView(DetailView):
  model = List

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('list') }: { self.object.name } { _('by') } { self.object.user }"
    return context

class AddList(CreateView):
  model = List
  fields = ['name', 'description', 'visibility']

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
  fields = ['name', 'description', 'visibility']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('lists') }: { _('edit list') }: { self.object.name }"
    return context
      
  def form_valid(self, form):
    messages.add_message(self.request, messages.SUCCESS, f"List \"{ form.instance.name }\" has been updated.")
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
class AddLocationToList(UpdateView):
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
      list = List.objects.get(slug=self.kwargs['slug'])
      location = Location.objects.get(slug=self.kwargs['location'])
    elif self.request.GET.get('list', ''):
      list = List.objects.get(slug=self.request.GET.get('list', ''))
      location = Location.objects.get(slug=self.kwargs['slug'])
    
    ''' Add as last item on the list, add self.steps to the last order entry '''
    order = list.locations.last().order + self.steps if list.locations.count() > 0 else self.steps
    ''' Only allow action from Comment User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      ''' Check if location is not most recent location '''
      if list.locations.all().count() > 0:
        if location == list.locations.all().last().location:
          messages.add_message(self.request, messages.ERROR, f"\"{ location.name }\" { _('was not added to list') } { list.name }. { _('This is already the last location on the list') }.")
          return redirect('location:list', list.slug)
      ''' It is safe to store location '''
      listlocation = ListLocation.objects.create(list=list, 
                                                  location=location, 
                                                  order=order,
                                                  user=self.request.user)
      messages.add_message(self.request, messages.SUCCESS, f"{ _('Added') } \"{ location.name }\"  { _('to list')} \"{ list.name }\".")
      ''' Check if distances should be calculated '''
      previous = listlocation.getPreviousLocation()
      if previous:
        ''' Store distance to previous location '''
        previous = previous.location
        distance = ListDistance.objects.get_or_create(origin=previous,
                                                      destination=location,
                                                      user=self.request.user,
                                                      )
        if not distance[0].hasData():
          distance[0].getData(request=self.request)
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
        location.delete()
        messages.add_message(self.request, messages.SUCCESS, f"{ _('Removed') } \"{ location.location.name }\"  { _('from list')} \"{ list.name }\". <a href=\"{reverse('location:AddLocationToList', args=[list.slug, location.location.slug])}\">{ _('Undo') }</a>.")
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
      if list.locations.count() == 0 or first != self.request.user.profile.home.last():
        ListLocation.objects.create(list=list,
                                    location=self.request.user.profile.home.last(),
                                    order=self.order,
                                    user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, f"{ list.name } { _('now departs from')} { self.request.user.profile.home.last() }")
        distance = ListDistance.objects.get_or_create(origin=self.request.user.profile.home.last(),
                                                      destination=first,
                                                      user=self.request.user,
                                                      )
        if not distance[0].hasData():
          distance[0].getData(request=self.request)
      else:
        messages.add_message(self.request, messages.INFO, f"{ list.name } { _('already departs from')} { self.request.user.profile.home.last() }")
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
    last = list.locations.last().location
    order = list.locations.last().order + self.steps if list.locations.count() > 0 else self.steps
    ''' Compare first entry with home of user'''
    ''' Only allow action from List User or Staff'''
    if list.user == self.request.user or self.request.user.is_superuser:
      if list.locations.count() == 0 or last != self.request.user.profile.home.last():
        ListLocation.objects.create(list=list,
                                    location=self.request.user.profile.home.last(),
                                    order=order,
                                    user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, f"{ list.name } { _('now ends at')} { self.request.user.profile.home.last() }")
        distance = ListDistance.objects.get_or_create(origin=last,
                                                      destination=self.request.user.profile.home.last(),
                                                      user=self.request.user,
                                                      )
        if not distance[0].hasData():
          distance[0].getData(request=self.request)
      else:
        messages.add_message(self.request, messages.INFO, f"{ list.name } { _('already ends at')} { self.request.user.profile.home.last() }")
    else:
      ''' Share errormessage that the list cannot be modified '''
      messages.add_message(self.request, messages.ERROR, f"{ _('List') } \"{ list }\" { _('cannot be modified')}. { _('This is not your list') }.")
    return redirect('location:list', self.kwargs['slug'])