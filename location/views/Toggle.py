from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.text import slugify
from django.db.models import CharField, BooleanField, ManyToManyField


# from django.db.models import ManyToManyField, ForeignKey, BooleanField

from django.contrib.auth.models import User

from location.models.Location import Location, Category, Chain
from location.models.Profile import Profile, VisitedIn
from location.models.Tag import Tag
from location.models.Comment import Comment
# from location.models.Media import Media

''' Toggle View
    - Toggle a value for a specific object
    @param location the location the attribute is toggled for
    @param attribute the attribute that is toggled
    @param value the value that is toggled
           If no value is provided, the location will be toggled in the
           default attribute of the object
    @return JSON response or redirect
    
'''
class ToggleAttribute(UpdateView):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.location = False
    self.attribute = False
    self.value = False

  def get_success_url(self) -> str:
    if not self.get_attribute():
      return reverse_lazy('location:home')
    elif self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
      if hasattr(self.get_location(), 'slug'):
        return reverse_lazy('location:getAttributesFor', kwargs={'location': self.get_location().slug, 'attribute': self.get_attribute('attribute')})
      else:
        return reverse_lazy('location:getAttributesFor', kwargs={'location': self.kwargs['slug'], 'attribute': self.get_attribute('attribute')}),
    elif self.get_attribute('success-url'):
      return self.get_attribute('success-url')
    return self.get_location().get_absolute_url()
  
  def get_location(self):
    if self.location == False:
      try:
        self.location = Location.objects.get(slug=self.kwargs['slug']) if 'slug' in self.kwargs else None
      except Location.DoesNotExist:
        self.location = False
    return self.location
  
  ''' Get Attribute 
      Get the attribute that is toggled
      - from the URL
      - from the POST request
      - from the GET request
  '''
  def get_attribute(self, key=None):
    mapping = {
      'tag': {
        'model': Tag, 
        'field': 'tags', 
        'target': 'tagslist', 
        'name': _('tag'), 
      }, 
      'category': {
        'model': Category, 
        'field': 'additional_category', 
        'target': 'categorylist', 
        'name': _('category'), 
      },
      'chain': {
        'model': Chain, 
        'field': 'chain', 
        'target': 'chainlist', 
        'name': _('chain'), 
      },
      'favorite': {
        'model': Location, 
        'field': 'favorite',
        'target': 'actionlist', 
        'name': _('favorite'), 
        'switch': True,
        'default': Profile.objects.get_or_create(user=self.request.user)[0],
      },
      'dislike': {
        'model': Location, 
        'field': 'least_liked', 
        'target': 'actionlist', 
        'name': _('least-liked'), 
        'switch': True,
        'default': Profile.objects.get(id=self.request.user.profile.id),
      },
      'maps-permission': {
        'model': Profile, 
        'field': 'maps_permission', 
        'target': 'maps-permission', 
        'name': _('maps-permission'), 
        'switch': True,
        'default': Profile.objects.get(id=self.request.user.profile.id),
        'success-url': reverse_lazy('location:profile'),
        'undo-url': reverse_lazy('location:ToggleAttribute', kwargs={'slug': 'profile', 'attribute': 'maps-permission'}),
      },
      'show-category-label': {
        'model': Profile, 
        'field': 'show_category_label', 
        'target': 'show-category-label', 
        'name': _('show-category-label'), 
        'switch': True,
        'default': Profile.objects.get(id=self.request.user.profile.id),
        'success-url': reverse_lazy('location:profile'),
        'undo-url': reverse_lazy('location:ToggleAttribute', kwargs={'slug': 'profile', 'attribute': 'show-category-label'}),
      },
      'filter-by-distance': {
        'model': Profile, 
        'field': 'filter_by_distance', 
        'target': 'filter-by-distance',
        'name': _('filter-by-distance'),
        'switch': True,
        'default': Profile.objects.get(id=self.request.user.profile.id),
        'success-url': reverse_lazy('location:profile'),
        'undo-url': reverse_lazy('location:ToggleAttribute', kwargs={'slug': 'profile', 'attribute': 'filter-by-distance'}),
      },
      'hide-least-liked': {
        'model': Profile, 
        'field': 'hide_least_liked', 
        'target': 'hide-least-liked',
        'name': _('hide-least-liked'),
        'switch': True,
        'default': Profile.objects.get(id=self.request.user.profile.id),
        'success-url': reverse_lazy('location:profile'),
        'undo-url': reverse_lazy('location:ToggleAttribute', kwargs={'slug': 'profile', 'attribute': 'hide-least-liked'}),
      },
    }
    if self.attribute == False:
      attribute = None
      if 'attribute' in self.kwargs:
        attribute = self.kwargs['attribute']
      elif self.request.POST.get('attribute', False):
        attribute = self.request.POST.get('attribute', None)
      elif self.request.GET.get('attribute', False):
        attribute = self.request.GET.get('attribute', None)
      self.attribute = mapping[attribute] if attribute in mapping else None
      if self.attribute == None:
        return False
      self.attribute['attribute'] = attribute
    ''' Return the attribute or a specific key '''
    if key != None:
      if key in self.attribute:
        return self.attribute[key]
      else:
        return False
    return self.attribute
  
  ''' Get Value
      Get the value that is toggled
      - from the URL
      - from the POST request
      - from the GET request
  '''
  def get_value(self):
    if self.value == False:
      value = None
      if 'value' in self.kwargs:
        value = self.kwargs['value']
      elif self.request.POST.get('value', False):
        value = self.request.POST.get('value', None)
      elif self.request.GET.get('value', False):
        value = self.request.GET.get('value', None)
      ''' Fetch value object '''
      if self.get_attribute() != None:
        model = self.get_attribute()['model']
        ''' Handle Parent/Child relations '''
        parent = None
        if value and ':' in value:
          parent, value = value.split(':')
          parent = self.get_attribute('model').objects.get_or_create(slug=slugify(parent), defaults={'name': parent.capitalize(), 'user': self.request.user})[0] if parent != None else None
        ''' Fetch or create value object '''
        if 'parent' in [field.name for field in model._meta.get_fields()]:  
          if 'slug' in [field.name for field in model._meta.get_fields()]:
            value = self.get_attribute('model').objects.get_or_create(slug=slugify(value), defaults={'name': value.title(), 'user': self.request.user, 'parent': parent}) if value != None else None
          else:
            value = self.get_attribute('model').objects.get_or_create(pk=value, defaults={'name': value.title(), 'user': self.request.user, 'parent': parent}) if value != None else None
        else:
          if 'slug' in [field.name for field in model._meta.get_fields()]:
            value = self.get_attribute('model').objects.get_or_create(slug=slugify(value), defaults={'name': value.title(), 'user': self.request.user}) if value != None else None
          else:
            value = self.get_attribute('model').objects.get_or_create(pk=value, defaults={'name': value.title(), 'user': self.request.user}) if value != None else None
        self.value = value[0] if value != None else None
    return self.value
    
  def get(self, request, *args, **kwargs):
    message = ''
    status = 200
    object = self.get_location()
    attribute = self.get_attribute()
    value = self.get_value() 
    ''' Verify Location'''
    if object == None:
      message = f"[023] { _('No location found with slug {}').format(self.kwargs['slug']) }"
      status = 404
    ''' Verify Attribute '''
    if attribute == None:
      message = f"[122] { _('Attribute is missing') }"
      status = 500
    elif attribute == False:
      message = f"[122] { _('Attribute not supported') }"
      status = 404
    ''' Verify Value '''
    if value == None and self.get_attribute('default') == None:
      message = f"[215] { _('Value is missing') }"
      status = 500
    elif value == False:
      message = f"[148] { _('Value not found') }"
      status = 404
    ''' Toggle '''
    if status == 200:
      ''' Understand the query to be executed based on the parameters 
          so store the actionable parameters in variables
      '''
      ''' Handle switch exceptions '''
      if self.get_attribute('switch'):
        value = object
        object = self.get_attribute('default') if self.get_value() == None else self.get_value()
      elif self.value == None and self.get_attribute('default') != None:
        value = self.get_attribute('default')
      print("Start detection")
      ''' Detect Toggle Field Type '''
      field = object._meta.get_field(attribute['field'])
      if isinstance(field, BooleanField):
        ''' Toggle Boolean Field '''
        print("Toggle Boolean Field")
        try:
          setattr(object, attribute['field'], not getattr(object, attribute['field']))
          object.save()
          message = _('Toggled {} to {}').format(attribute['name'], getattr(object, attribute['field']))
        except Exception as e:
          message = f"[157] { _('Error when toggling {} of {}: {}').format(attribute['name'], object, escape(e)) }"
          status = 500
      elif isinstance(field, ManyToManyField):
        print("Toggle ManyToMany Field")
        ''' Toggle ManyToMany Field '''
        if value in getattr(object, attribute['field']).all():
          getattr(object, attribute['field']).remove(value)
          message = _('Removed {} from {} {}').format(value.name, attribute['name'], object.name)
        else:
          ''' Value should be added '''
          try:
            getattr(object, attribute['field']).add(value)
            message = _('Added {} to {} {}').format(value, attribute['name'], object)
          except Exception as e:
            message = f"[157] { _('Error when adding {} to {} of {}: {}').format(value, attribute['name'], object, escape(e)) }"
            status = 500
    else:
      ''' Toggeling field type not supported '''
      message = f"[292] { _('status attribute not supported for {}').capitalize().format(object) }"
      status = 500
    ''' Build Undo-URL  '''
    if not attribute:
      url = ''
    elif self.get_attribute('undo-url'):
      url = self.get_attribute('undo-url')
    elif self.value == None:
      url = reverse_lazy("location:ToggleAttribute", kwargs={"slug": self.kwargs['slug'], "attribute": self.kwargs['attribute']})
    else:
      url = reverse_lazy("location:ToggleAttributeValue", kwargs={"slug": self.kwargs['slug'], "attribute": self.kwargs['attribute'], 'value': self.get_value().slug})
    ''' Build response '''
    if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
      ''' If request is triggered via AJAX, return JSON response '''
      response = {
        'success-url': self.get_success_url(),
        'target': self.get_attribute('target'),
        'message': message + f'. (<a href="{ url }" class="toggable">{ _("undo").capitalize() }</a>)',
      }
      return JsonResponse(response, status=status)
    else:
      ''' Else, add message to queue and return to location '''
      if status == 200:
        message = escape(message) + f'. (<a href="{ url }" class="toggable">{ _("undo").capitalize() }</a>)'
        messages.add_message(self.request, messages.SUCCESS, message)
      else:
        messages.add_message(self.request, messages.ERROR, message)
      ''' Build redirect URL '''
      return redirect(self.get_success_url())


''' Toggle Exceptions '''
class ToggleDeleted(UpdateView):
  # /toggle/<model>/<pk>/
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.model = None
    self.object = None
    self.kwargs = kwargs
    self.models = {
      'visit': {
        'model': VisitedIn, 
        'success_url': redirect('location:profile'),
        'ajax_success_url': False,
        'ajax_target': False,
      },
      'comment': {
        'model': Comment,
        'success_url': 'location:location',
        'ajax_success_url': 'location:getAttributesFor',
        'ajax_target': 'commentlist',
      },
      'tag': {
        'model': Tag,
        'success_url': 'location:tags',
        # 'ajax_success_url': 'location:getAttributesFor',
        # 'ajax_target': 'tagslist',
      },
    }

  def get_model(self):
    if self.model == None:
      if self.kwargs['model'].lower().strip() in self.models:
        self.model = self.models[self.kwargs['model'].lower().strip()]['model'] if self.kwargs['model'] in self.models else None
    return self.model
  
  def get_object(self):
    if self.object == None:
      if self.get_model():
        model = self.get_model()
        if 'slug' in [field.name for field in model._meta.get_fields()]:
          object = self.get_model().objects.get(slug=self.kwargs['pk'])
        else:
          object = self.get_model().objects.get(pk=self.kwargs['pk'])
        self.object = object
      else:
        self.object = None
    return self.object
  
  def get_success_url(self):
    if self.get_attribute('success_url'):
      return redirect(self.get_attribute('success_url'))
    elif self.models[self.kwargs['model'].lower().strip()]['success_url']:
      if hasattr(self.get_object(), 'location'):
        return redirect(self.models[self.kwargs['model'].lower().strip()]['success_url'], self.get_object().location.slug)
      else:
        return redirect(self.models[self.kwargs['model'].lower().strip()]['success_url'])
    return None
  
  def get_ajax_success_url(self):
    if self.get_attribute('success_url'):
      return redirect(self.get_attribute('success_url'))
    elif self.models[self.kwargs['model'].lower().strip()]['ajax_success_url']:
      if hasattr(self.get_object(), 'location'):
        return reverse_lazy(self.models[self.kwargs['model'].lower().strip()]['ajax_success_url'], kwargs={'location': self.get_object().location.slug, 'attribute': 'comment'})
      else:
        return reverse_lazy(self.models[self.kwargs['model'].lower().strip()]['ajax_success_url'])
    return None
  def get_ajax_target(self):
    return self.models[self.kwargs['model'].lower().strip()]['ajax_target']
  
  def get(self, request, *args, **kwargs):
    message = ''
    status = 200
    if self.get_model() == None:
      ''' Verify Model'''
      message = f"[729] { _('no model found for {}').capitalize().format(self.kwargs['model']) }"
      status = 500
    elif self.get_object() == None:
      ''' Verify Object '''
      message = f"[282] { _('object {} not found').capitalize().format(self.kwargs['pk']) }"
      status = 404
    else:
      ''' Toggle '''
      object = self.get_object()
      if hasattr(object, 'status'):
        if object.status == 'x':
          ''' Object should be restored '''
          object.status = 'p'
          message = _('restored {}').format(object)
        else:
          ''' Object should be removed '''
          object.status = 'x'
          message = _('removed {}').format(object)
        object.save()
      else:
        message = f"[292] { _('status attribute not found for {}').capitalize().format(object) }"
        status = 500
    ''' Build response '''
    ''' Build Undo-link '''
    url = reverse_lazy("location:ToggleDeleted", kwargs={"model": self.kwargs['model'], "pk": self.kwargs['pk']})
    message = escape(message) + f'. (<a href="{ url }" class="toggable">{ _("undo").capitalize() }</a>)'
    ''' If request is triggered via AJAX, return JSON response '''
    if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' and self.get_ajax_success_url():
      ''' If request is triggered via AJAX, return JSON response '''
      response = {
        'success-url': self.get_ajax_success_url(),
        'target': self.get_ajax_target(),
        'message': message,
      }
      return JsonResponse(response, status=status)
    else:
      ''' Else, add message to queue and return to location '''
      if status == 200:
        messages.add_message(self.request, messages.SUCCESS, message)
      else:
        messages.add_message(self.request, messages.ERROR, message)
      return self.get_success_url()

  
# ''' Toggle Family Member '''
# class ToggleFamilyMember(UpdateView):
#   model = User
#   fields = ['id']

#   def get(self, request, *args, **kwargs):
#     family_member = User.objects.get(id=kwargs['id'])
#     if hasattr(self.request.user, 'profile'):
#       profile = self.request.user.profile
#     else:
#       profile = Profile.objects.create(user=self.request.user)
#       messages.add_message(self.request, messages.INFO, f"Created profile for { self.request.user.get_full_name() }")
#     ''' If User is already a family member '''
#     if family_member in profile.family.all():
#       profile.family.remove(family_member)
#       messages.add_message(self.request, messages.SUCCESS, f"{ _('Removed') } { family_member.get_full_name() } { _('from family') }.")
#     else:
#       profile.family.add(family_member)
#       messages.add_message(self.request, messages.SUCCESS, f"{ _('Added') } { family_member.get_full_name() } { _('to family') }.")
#     return redirect('location:profile')
  
# class ToggleMediaDeleted(ToggleView):
#   model = Media
#   fields = ['status']

#   def get_success_url(self) -> str:
#     return reverse_lazy('location:MediaStack', kwargs={'slug': self.get_object().location.slug})
  
#   def handle_exceptions(self, object_slug):
#     return redirect('location:MediaStack', self.get_object().location.slug)
    
#   def toggle(self, object_slug):
#     try:
#       object = Media.objects.get(location__slug=self.kwargs['object_slug'], id=self.kwargs['pk'])
#     except Media.DoesNotExist:
#       messages.add_message(self.request, messages.ERROR,
#                            f"{ _('can not find media with id ')} { object_slug }")
#       return redirect(self.get_success_url())
#     if object.status != 'x':
#       ''' Media should be removed '''
#       object.status = 'x'
#       messages.add_message(self.request, messages.SUCCESS,
#                            f"{ _('removed') } { _('media') } { object.title } { _('from') } { object.location.name }.")
#     else:
#       ''' Chain should be added '''
#       object.status = 'p'
#       messages.add_message(self.request, messages.SUCCESS,
#                            f"{ _('restored') } { _('media') } { object.title } { _('to') } { object.location.name }.")
#     object.save()