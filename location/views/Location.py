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

from location.models.Location import Location, Category, Chain, Link
from location.models.Comment import Comment
from location.models.Tag import Tag
from location.models.List import List, ListLocation
from location.models.Profile import VisitedIn


''' MASTER VIEWS '''
''' Location Master
    Class that holds the functionality that is used in the Location List view,
    Activity List view and Search view.
'''
class LocationMasterView:
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Active filters '''
    context['active_filters'] = {}
    ''' URL Structured filters: Country, region and department '''
    if 'country' in self.kwargs:
      context['active_filters']['country'] = self.kwargs['country']
    if 'region' in self.kwargs:
      context['active_filters']['region'] = self.kwargs['region']
    if 'department' in self.kwargs:
      context['active_filters']['department'] = self.kwargs['department']
    ''' URL queryset filters '''
    context['active_filters']['query'] = {}
    if self.request.GET.get('category', ''):
      for category in self.request.GET.get('category', '').split(','):
        if 'category' not in context['active_filters']['query']:
          context['active_filters']['query']['category'] = []
        context['active_filters']['query']['category'].append(category)
    if self.request.GET.get('tag', ''):
      for tag in self.request.GET.get('tag', '').split(','):
        if 'tag' not in context['active_filters']['query']:
          context['active_filters']['query']['tag'] = []
        context['active_filters']['query']['tag'].append(tag)
    if self.request.GET.get('chain', ''):
      for chain in self.request.GET.get('chain', '').split(','):
        if 'chain' not in context['active_filters']['query']:
          context['active_filters']['query']['chain'] = []
        context['active_filters']['query']['chain'].append(chain)
    if self.request.GET.get('q', ''):
      context['q'] = self.request.GET.get('q', '')
    return context

  def filter_queryset(self, queryset):
    ''' Process Location filters '''
    if 'country' in self.kwargs:
      queryset = queryset.filter(location__parent__parent__slug__iexact=self.kwargs['country'])
    if 'region' in self.kwargs:
      queryset = queryset.filter(location__parent__slug__iexact=self.kwargs['region'])
    if 'department' in self.kwargs:
      queryset = queryset.filter(location__slug__iexact=self.kwargs['department'])
    ''' Process Category filters '''
    if self.request.GET.get('category', ''):
      categories = self.request.GET.get('category', '').split(',')
      queryset = queryset.filter(category__slug__in=categories) | queryset.filter(additional_category__slug__in=categories)
    ''' Process Tag filters '''
    if self.request.GET.get('tag', ''):
      tags = self.request.GET.get('tag', '').split(',')
      queryset = queryset.filter(tags__slug__in=tags)
    ''' Process Chain filters '''
    if self.request.GET.get('chain', ''):
      chain = self.request.GET.get('chain', '').split(',')
      queryset = queryset.filter(chain__slug__in=chain) | queryset.filter(chain__parent__slug__in=chain)
    ''' Process the dislike filter '''
    if hasattr(self.request.user, 'profile'):
      if self.request.user.profile.hide_least_liked:
        queryset = queryset.exclude(slug__in=self.request.user.profile.least_liked.values_list('slug', flat=True))
    ''' Process ?q= filters '''
    if self.request.GET.get('q', ''):
      query = self.request.GET.get('q', '').split(' ')
      for q in query:
        queryset = queryset.filter(name__icontains=q) |\
                   queryset.filter(address__icontains=q) |\
                   queryset.filter(owners_names__icontains=q) |\
                   queryset.filter(description__icontains=q) |\
                   queryset.filter(category__name__icontains=q) |\
                   queryset.filter(additional_category__name__icontains=q) |\
                   queryset.filter(chain__name__icontains=q) |\
                   queryset.filter(chain__parent__name__icontains=q) |\
                   queryset.filter(tags__name__icontains=q) |\
                   queryset.filter(location__name__icontains=q) |\
                   queryset.filter(location__parent__name__icontains=q) |\
                   queryset.filter(location__parent__parent__name__icontains=q)
    return queryset


''' EditLocationMaster
    Holds the functionality that is used in both Location as well as Avtivity update page
'''
class EditLocationMaster(UpdateView):
  model = Location
  fields = ['name', 'website', 'link', 'description', 'category', 'additional_category', 'visibility', 'address', 'phone', 'owners_names', 'chain']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('edit') }: { self.object .name}"
    ''' Categories '''
    if self.get_object().isActivity():
      context['categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
      context['additional_categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).exclude(slug=self.get_object().category.slug).exclude(slug='home').exclude(secondary_for=self.object).order_by('name')
    else:  
      #if self.request.resolver_match.view_name == 'location:AddActivity':
      context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
      context['additional_categories'] = Category.objects.exclude(slug=settings.ACTIVITY_SLUG).exclude(parent__slug=settings.ACTIVITY_SLUG).exclude(slug=self.get_object().category.slug).exclude(secondary_for=self.object).order_by('name')
    ''' Tags '''
    context['available_tags'] = Tag.objects.exclude(locations=self.object).exclude(children__gt=1).order_by('parent__name', 'name')
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
def CreatCategories(request):
  parent = None
  for category in ['Home', 'Camping', 'Hotel', 'Bed & Breakfast', 'Chambre D\'Hôtes', 'Safaritent', 'Gite']:
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
''' LIST VIEWS '''

''' Location List '''
class LocationListView(LocationMasterView, ListView):
  model = Location

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Scope '''
    context['scope'] = 'locations'
    ''' Available filters '''
    context['available_filters'] = {
      # 'category':     Category.objects.exclude(parent__slug=settings.ACTIVITY_SLUG).exclude(slug=settings.ACTIVITY_SLUG),
      'category':     self.get_queryset().values_list('category__slug', 'category__name').order_by().distinct(),
      'tag':          self.get_queryset().values_list('tags__slug', 'tags__name').exclude(tags__slug__isnull=True).distinct().order_by(),
    }
    return context

  def get_queryset(self):
    ''' Fetch all published locations '''
    queryset = Location.objects.filter(status='p').exclude(category__slug=settings.ACTIVITY_SLUG).exclude(category__parent__slug=settings.ACTIVITY_SLUG)
    queryset = filter_visibility(self.request.user, queryset)
    queryset = self.filter_queryset(queryset)
    ''' Result Ordering '''
    queryset = queryset.order_by('location__parent__parent', 'location__parent', 'location__name').distinct()
    return queryset

class ActivityListView(LocationMasterView, ListView):
  model = Location

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Scope '''
    context['scope'] = 'activities'
    ''' Available filters '''
    context['available_filters'] = {
      'category':     self.get_queryset().values_list('category__slug', 'category__name').order_by().distinct(),
      'tag':          self.get_queryset().values_list('tags__slug', 'tags__name').exclude(tags__slug__isnull=True).distinct().order_by(),
    }
    return context

  def get_queryset(self):
    ''' Fetch all published locations '''
    queryset = Location.objects.filter(status='p')
    queryset = queryset.filter(category__slug=settings.ACTIVITY_SLUG) | queryset.filter(category__parent__slug=settings.ACTIVITY_SLUG)
    queryset = filter_visibility(self.request.user, queryset)
    queryset = self.filter_queryset(queryset)
    ''' Result Ordering '''
    queryset = queryset.order_by('location__parent__parent', 'location__parent', 'location__name')
    return queryset

class LocationSearchView(LocationMasterView, ListView):
  model = Location
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Scope '''
    context['scope'] = _('locations')
    ''' Available filters '''
    context['available_filters'] = {
      'category':     self.get_queryset().values_list('category__slug', 'category__name').order_by().distinct(),
      'tag':          self.get_queryset().values_list('tags__slug', 'tags__name').exclude(tags__slug__isnull=True).distinct().order_by(),
    }
    return context

  def get_queryset(self):
    ''' Fetch all published locations and activities '''
    queryset = Location.objects.filter(status='p')
    ''' Add private objects for current user to queryset '''
    if self.request.user.is_authenticated:
      queryset |= Location.objects.filter(status='c')
      queryset |= Location.objects.filter(status='-', user=self.request.user)
      ''' Exclude home other than mine '''
      queryset = queryset.exclude(category__name='Home')
      if hasattr(self.request.user, 'profile'):
        queryset |= Location.objects.filter(home_of=self.request.user.profile)
    ''' Apply filtering based on url or query parameters'''
    queryset = self.filter_queryset(queryset)
    ''' Result Ordering '''
    queryset = queryset.order_by('location__parent__parent', 'location__parent', 'location__name').distinct()
    return queryset

''' DETAIL VIEWS '''

''' Location Detail View '''  
class LocationView(DetailView):
  model = Location

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ''' Scope '''
    context['scope'] = f"{ _(self.object.getCategory()) }: { self.object.name }"
    ''' Comments '''
    comments = Comment.objects.filter(location__slug=self.object.slug, status='p')
    if self.request.user.is_authenticated:
      comments =  comments.filter(visibility__in='a,c') |\
                  comments.filter(visibility='p', user=self.request.user) |\
                  comments.filter(visibility='f', user__profile__family=self.request.user) |\
                  comments.filter(visibility='f', user=self.request.user)
    else:
      comments = comments.filter(visibility='a')
      context['could_have_comments'] = Comment.objects.filter(location__slug=self.object.slug, status='p', visibility='c')
    ''' Lists '''
    lists = ListLocation.objects.filter(list__status='p', location=self.object)
    available_lists = List.objects.filter(status='p')
    if self.request.user.is_authenticated:
      lists = lists.filter(list__visibility__in='p,c') |\
              lists.filter(list__visibility='f', list__user__profile__family=self.request.user) |\
              lists.filter(list__visibility__in='f,q', list__user=self.request.user)
      available_lists = available_lists.filter(visibility__in='p,c') |\
                        available_lists.filter(visibility='f', user__profile__family=self.request.user) |\
                        available_lists.filter(visibility__in='f,q', user=self.request.user)
    else:
      lists = lists.filter(list__visibility='p')
      available_lists = available_lists.filter(visibility='p')
    lists = lists.order_by('list__name').distinct()
    available_lists = available_lists.exclude(locations__location=self.object).order_by().distinct()
    context['lists'] = lists
    
    context['available_lists'] = available_lists
    ''' Tags '''
    context['tags'] = Tag.objects.filter(locations__slug=self.object.slug).order_by('list_as', 'name').distinct()
    context['comments'] = comments.order_by('-date_added').distinct()
    if self.get_object().visibility == 'f':
      if hasattr(self.get_object().user, 'profile'):
        context['family'] = self.get_object().user.profile.family.all()
    context['visitors'] = self.get_visitors()
    return context
  
  def get_visitors(self):
    result = VisitedIn.objects.filter(user=self.request.user, location=self.get_object())
    result = filter_visibility(self.request.user, result)
    return result

''' CREATE VIEWS '''

class AddLocation(CreateView):
  model = Location
  fields = ['name', 'website', 'description', 'category', 'visibility']
  
  def get_context_data(self, **kwargs):
    if Category.objects.all().count() == 0:
      CreatCategories(self.request)
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
    elif 'google' not in form.instance.website:
      link = Link.objects.get_or_create(url=f'https://google.com/search?q={ form.cleaned_data["name"] }', defaults={'user': self.request.user})
      form.instance.link.add(link[0].id)
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
      CreatCategories(self.request)
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
    context['categories'] = Category.objects.filter(parent__slug=settings.ACTIVITY_SLUG).order_by('name')
    if self.request.user.is_authenticated:
      context['categories'] |= Category.objects.filter(slug='home')
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