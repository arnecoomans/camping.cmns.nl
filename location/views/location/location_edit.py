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
  fields = ['name', 'website', 'link', 'description', 'category', 'additional_category', 'visibility', 'address', 'phone', 'owners_names', 'chain']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('edit') }: { self.object .name}"
    ''' Categories '''
    context['additional_categories'] = Category.objects.exclude(slug=self.get_object().category.slug).exclude(secondary_for=self.object).order_by('parent__name', 'name')
    if self.get_object().isActivity():
      context['categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    else:  
      context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
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
    if str(form.instance.category).lower() == 'home' and form.instance.visibility != 'f':
      form.instance.visibility = 'f'
      messages.add_message(self.request, messages.INFO, f"{ _('visibility of your home is set to family') }.") 
    ''' Ensure URL is stored for this location '''
    if not form.instance.website:
      form.instance.website = f'https://google.com/search?q={ form.instance.name }'
    elif 'google' not in form.instance.website:
      link = Link.objects.get_or_create(url=f'https://google.com/search?q={ form.cleaned_data["name"] }', defaults={'user': self.request.user})
      form.instance.link.add(link[0].id)
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
      messages.add_message(self.request, messages.SUCCESS, f"{ _('changed information of location') } \"{form.instance.name }\".")
      form.save()
    else:
      ''' No changes are detected, redirect to image without saving. '''
      messages.add_message(self.request, messages.WARNING, f"{ _('no changed made to') } \"{ form.instance.name }\".")
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
  fields = ['name', 'website', 'description', 'category', 'visibility']
  
  def get_context_data(self, **kwargs):
    if Category.objects.all().count() == 0:
      CreateCategories(self.request)
    context = super().get_context_data(**kwargs)
    if self.request.resolver_match.view_name == 'location:AddActivity':
      context['scope'] = 'activity'
      context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    else:
      context['scope'] = 'location'
      context['categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    return context

  def form_valid(self, form):
    ''' Force Home to be set to Family '''
    if str(form.instance.category).lower() == 'home' and form.instance.visibility != 'f':
      form.instance.visibility = 'f'
      messages.add_message(self.request, messages.INFO, f"{ _('visibility of your home is set to family') }.") 
    if not form.instance.website:
      ''' If no website is submitted, store a Google Search for this location name'''
      form.instance.website = f'https://google.com/search?q={ form.instance.name }'
    # elif 'google' not in form.instance.website:
    #   link = Link.objects.get_or_create(url=f'https://google.com/search?q={ form.cleaned_data["name"] }', defaults={'user': self.request.user})
    #   form.instance.link.add(link[0].id)
    try:
      location = Location.objects.create(
        slug = slugify(form.instance.name),
        name = form.instance.name,
        website = form.instance.website,
        description = form.instance.description,
        category = form.instance.category,
        visibility= form.instance.visibility,
        status = form.instance.status,
        user=self.request.user,
      )
    except IntegrityError as e:
      suggested_location = Location.objects.get(name__iexact=form.instance.name)
      messages.add_message(self.request, messages.ERROR, f"{ _('failed to add new location') }: \"{ form.instance.name }\". { _('A location with this name already exists:') } <a href=\"{ reverse('location:location', kwargs={'slug': suggested_location.slug}) }\">{ suggested_location.name }</a>")
      return redirect('location:AddLocation')
    messages.add_message(self.request, messages.SUCCESS, f"{ _('added new location') }: \"{ location.name }\"")
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