from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.db import IntegrityError
from django.conf import settings

from ..snippets.filter_class import FilterClass

from location.models.Location import Location, Category, Chain, Link
from location.models.Tag import Tag
from location.models.List import ListDistance


''' MASTER VIEWS '''
''' Location Master
    Class that holds the functionality that is used in the Location List view,
    Activity List view and Search view.
'''

''' EditLocationMaster
    Holds the functionality that is used in both Location as well as Avtivity update page
'''
class EditLocationMaster(UpdateView, FilterClass):
  model = Location
  fields = ['name', 'link', 'description', 'category', 'additional_category', 'visibility', 'status', 'address', 'phone', 'owners_names', 'chain']
  template_name = 'location/location/location_form.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('edit') }: { self.object .name}"
    ''' Categories '''
    context['additional_categories'] = Category.objects.exclude(slug=self.get_object().category.slug).exclude(secondary_for=self.object).order_by('parent__name', 'name')
    if self.get_object().isActivity():
      context['categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    else:  
      context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    ''' Links '''
    context['links'] = self.get_links()
    ''' Tags '''
    tags = Tag.objects.filter(locations__slug=self.object.slug)
    tags = self.filter_status(tags)
    tags = self.filter_visibility(tags)
    tags = tags.order_by('list_as', 'name').distinct()
    context['tags'] = tags
    available_tags = Tag.objects.exclude(locations=self.object).exclude(children__gt=1)
    available_tags = self.filter_status(available_tags)
    available_tags = self.filter_visibility(available_tags)
    available_tags = available_tags.order_by('parent__name', 'name')
    context['available_tags'] = available_tags
    ''' Chains '''
    context['available_chains'] = Chain.objects.filter(children=None).exclude(locations=self.object)
    return context

  ''' Get Links
  '''
  def get_links(self):
    links = self.object.link.all()
    links = self.filter_status(links)
    links = self.filter_visibility(links)
    links = links.order_by('-primary').distinct()
    return links

  def get_form(self):
    ''' Add User field for staff '''
    if self.request.user.is_staff == True:
      self.fields.append('user')
    form = super(EditLocationMaster, self).get_form()
    return form
  
  def form_invalid(self, form):
    messages.add_message(self.request, messages.WARNING, f"{ _('Form cannot be saved because of the following error(s)') }: { form.errors }")
    return super().form_invalid(form)
  
  def form_valid(self, form):
    ''' Force Home to be set to Family '''
    if str(form.cleaned_data['category']).lower() == 'home' and form.cleaned_data['visibility'] != 'f':
      form.cleaned_data['visibility'] = 'f'
      messages.add_message(self.request, messages.INFO, f"{ _('visibility of your home is set to family') }.") 
    ''' Only allow user change by superuser '''
    if not self.request.user.is_superuser and 'user' in form.changed_data: 
      ''' User change is initiated by non_superuser. 
          Fetch user from stored object and retain'''
      original = Location.objects.get(slug=self.kwargs['slug'])
      form.instance.user = original.user
      messages.add_message(self.request, messages.WARNING, f"{ _('you are not authorized to change the user. Keeping user') } \"{ original.user }\".")
    elif not form.instance.user:
      ''' If for some reason no user it set, set user to current user '''
      form.instance.user = self.request.user
    if len(form.changed_data) > 0:
      ''' Only if data has changed, save the Object '''
      messages.add_message(self.request, messages.SUCCESS, f"{ _('changed information of location') } \"{form.cleaned_data['name'] }\".")
      form.save()
    else:
      ''' No changes are detected, redirect to image without saving. '''
      messages.add_message(self.request, messages.WARNING, f"{ _('no changed made to') } \"{ form.cleaned_data['name'] }\".")
      return redirect(reverse_lazy('location:location', kwargs={'slug': self.object.slug}))
    return super().form_valid(form)
  

''' Special Functions'''
def CreateCategories(request):
  parent = None
  for category in ['Home', 'Camping', 'Hotel', 'Bed & Breakfast', 'Chambre D\'Hôtes', 'Safaritent', 'Gite', 'Caravan (rental)']:
    Category.objects.create(
      slug = slugify(category),
      name = category,
      parent = parent,
      user = request.user,
    )
  parent = Category.objects.create(
      slug = slugify('activity'),
      name = 'Activity',
      parent = parent,
      user = request.user,
    )
  for category in ['City', 'Village', 'Zoo', 'Theme-park', 'Museum', 'Park', 'Beach', 'Swimmingpool', 'Sight-to-see']:
    Category.objects.create(
      slug = slugify(category),
      name = category,
      parent = parent,
      user = request.user,
    )
''' CREATE VIEWS '''
class AddLocation(CreateView):
  model = Location
  template_name = 'location/location/location_form.html'
  fields = ['name', 'description', 'category', 'visibility']
  
  def get_context_data(self, **kwargs):
    if Category.objects.all().count() == 0:
      CreateCategories(self.request)
    context = super().get_context_data(**kwargs)
    context['scope'] = _('location or activity')
    context['categories'] = Category.objects.exclude(children__gt=1).order_by('parent', 'name')
    # if self.request.resolver_match.view_name == 'location:AddActivity':
    #   context['scope'] = 'activity'
    #   context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    # else:
    #   context['scope'] = 'location'
    #   context['categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    return context

  def form_valid(self, form):
    ''' Force Home to be set to Family '''
    if str(form.cleaned_data['category']).lower() == 'home' and form.cleaned_data['visibility'] != 'f':
      form.cleaned_data['visibility'] = 'f'
      messages.add_message(self.request, messages.INFO, f"{ _('visibility of your home is set to family') }.") 
    # if not form.cleaned_data['website']:
    #   ''' If no website is submitted, store a Google Search for this location name'''
    #   form.cleaned_data['website'] = f"https://google.com/search?q={ form.cleaned_data['name'] }"
    # elif 'google' not in form.instance.website:
    #   link = Link.objects.get_or_create(url=f'https://google.com/search?q={ form.cleaned_data["name"] }', defaults={'user': self.request.user})
    #   form.instance.link.add(link[0].id)
    try:
      location = Location.objects.create(
        slug = slugify(form.cleaned_data['name']),
        name = form.cleaned_data['name'],
        description = form.cleaned_data['description'] if 'description' in form.cleaned_data else '',
        category = form.cleaned_data['category'] if 'category' in form.cleaned_data else 'camping',
        visibility= form.cleaned_data['visibility'] if 'visibility' in form.cleaned_data else 'c',
        status = form.cleaned_data['status'] if 'status' in form.cleaned_data else 'p',
        user=self.request.user,
      )
      messages.add_message(self.request, messages.SUCCESS, f"{ _('added new location') }: \"{ location.name }\"")
      ''' Add link to Location '''
      if self.request.POST.get('link', False):
        link = Link.objects.get_or_create(url=self.request.POST.get('link', ''), defaults={
          'user': self.request.user,
          'title': self.request.POST.get('link-title', None)
          })
      else:
        link = Link.objects.get_or_create(url=f"https://google.com/search?q={ form.cleaned_data['name'] }", defaults={
          'user': self.request.user
          })  
      location.link.add(link[0])
      messages.add_message(self.request, messages.INFO, f"{ _('added link') }: \"{ link[0].get_title() }\" { _('to') } { location.name }.")
    except IntegrityError as e:
      suggested_location = Location.objects.get(name__iexact=form.cleaned_data['name'])
      messages.add_message(self.request, messages.ERROR, f"{ _('failed to add new location') }: \"{ form.cleaned_data['name'] }\". { _('A location with this name already exists:') } <a href=\"{ reverse('location:location', kwargs={'slug': suggested_location.slug}) }\">{ suggested_location.name }</a>")
      return redirect('location:AddLocation')
    ''' Since the object has been added, now we can automate fetch additional data '''
    location.getLatLng(self.request)
    location.getDistanceFromDepartureCenter(self.request)
    location.getRegion(self.request)
    return redirect('location:location', location.slug)


''' UPDATE VIEWS '''
  
class EditLocation(EditLocationMaster):
  def get_context_data(self, **kwargs):
    if Category.objects.all().count() == 0:
      CreateCategories(self.request)
    context = super().get_context_data(**kwargs)
    context['categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    if self.request.user.is_authenticated:
      context['categories'] |= Category.objects.filter(slug='home')
    return context

  def get_success_url(self):
    return reverse_lazy('location:location', kwargs={'slug': self.object.slug})
  
class EditActivity(EditLocationMaster):
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG) | Category.objects.filter(slug=settings.ACTIVITY_SLUG)
    context['categories'] = context['categories'].order_by('name')
    return context

  def get_success_url(self):
    return reverse_lazy('location:location', kwargs={'slug': self.object.slug})
  
class ResetLocationData(UpdateView):
  model = Location
  fields = ['location', 'coord_lat', 'coord_lng']

  def get(self, request, *args, **kwargs):
    if request.user.is_staff or request.user.is_superuser:
      ''' Drop stored data '''
      self.get_object().location = None
      self.get_object().coord_lng = None
      self.get_object().coord_lat = None
      ''' Fetch information again '''
      self.get_object().getLatLng(request)
      self.get_object().getDistanceFromDepartureCenter(request)
      self.get_object().getRegion(request)
      ''' If distance to home is calculated, remove distance to home '''
      if hasattr(self.request.user, 'profile') and self.request.user.profile.home:
        actions = 0
        try:
          distance_to_home = ListDistance.objects.get(origin=self.request.user.profile.home,
                                                      destination=self.get_object())
          distance_to_home.delete()
          actions += 1
        except:
          pass
        try:
          distance_to_home = ListDistance.objects.get(origin=self.get_object(),
                                                      destination=self.request.user.profile.home)
          distance_to_home.delete()
          actions += 1
        except:
          pass
        if actions > 0:
          messages.add_message(self.request, messages.INFO, f"{ _('removed distance to home') }.")
    return redirect('location:location', self.get_object().slug)

class GetDistanceToHome(DetailView):
  model = Location

  def get(self, request, *args, **kwargs):
    try:
      location = Location.objects.get(slug=self.kwargs['slug'])
    except Location.DoesNotExist:
      messages.add_message(self.request, messages.ERROR, f"{ _('location does not exist') }.")
      return redirect('location:locations')
    if hasattr(self.request.user, 'profile'):
      if location == self.request.user.profile.home:
        messages.add_message(self.request, messages.WARNING, f"{ _('cannot calculate distance for this location') }: { _('origin and destination are the same') }.")
      else:
        distance = ListDistance.objects.get_or_create(origin=self.request.user.profile.home,
                                                      destination=location,
                                                      defaults={
                                                        'user': self.request.user,
                                                      })
        distance[0].getData(self.request)
      return redirect('location:location', location.slug)


class addLinkToLocation(UpdateView):
  model = Location
  fields = ['link']

  def post(self, request, *args, **kwargs):
    location = self.get_object()
    url = request.POST.get('url', '')
    ''' Check if url is supplied '''
    if len(url) > 3:
      ''' Ensure url starts with http(s):// '''
      if not url.lower().startswith('http://') and not url.lower().startswith('https://'):
        url = f"https://{ url }"
      ''' See if link already exists '''
      links = Link.objects.filter(url__iexact=url)
      if len(links) > 0:
        ''' Link already exists, add it to location 
            It is safe to assume that the first link is the one we want to add
        '''
        self.get_object().link.add(links[0])
        ''' Check if fields need to be updated and save the data'''
        if request.POST.get('link-title', None):
          links[0].title = request.POST.get('link-title', None)
        links[0].visibility = request.POST.get('visibility', 'c')
        links[0].primary = True if request.POST.get('primary', False) else False
        links[0].save()  
        messages.add_message(self.request, messages.INFO, f"{ _('updated link') }: \"{ links[0].get_title() }\".")
      else:
        ''' Link does not exist, create it '''
        link = Link.objects.create(
          url=url,
          user=request.user,
          title=request.POST.get('link-title', None),
          visibility=request.POST.get('visibility', 'c'),
          primary=True if request.POST.get('primary', False) else False,
        )
        location.link.add(link)
        messages.add_message(self.request, messages.INFO, f"{ _('created and') } { _('added link') }: \"{ link.get_title() }\" to { location.name }.")
    else:
      messages.add_message(self.request, messages.ERROR, f"{ _('you did not supply a valid URL') }.")
    return redirect('location:EditLocation', self.get_object().slug)
    
class deleteLinkFromLocation(UpdateView):
  model = Location
  fields = ['link']

  def get(self, request, *args, **kwargs):
    if request.user == self.get_object().user or request.user.is_staff or request.user.is_superuser:
      link = Link.objects.get(id=self.kwargs['linkid'])
      self.get_object().link.remove(link)
      messages.add_message(self.request, messages.INFO, f"{ _('removed link') }: \"{ link.get_title() }\".")
    return redirect('location:EditLocation', self.get_object().slug)
  
class editLinkAtLocation(UpdateView):
  model = Link
  fields = ['url', 'title', 'visibility', 'primary']
  template_name = 'location/location/link_form.html'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['location'] = Location.objects.get(slug=self.kwargs['location_slug'])
    return context

  def get_success_url(self) -> str:
    return reverse('location:EditLocation', kwargs={'slug': self.kwargs['location_slug']})

  def get(self, request, *args, **kwargs):
    if request.user == self.get_object().user or request.user.is_staff or request.user.is_superuser:
      messages.add_message(self.request, messages.INFO, f"{ _('editing link') }: \"{ self.get_object().get_title() }\".")
      return super().get(request, *args, **kwargs)
    else:
      messages.add_message(self.request, messages.ERROR, f"{ _('you are not authorized to edit this link') }.")
      return redirect('location:EditLocation', self.kwargs['location_slug'])