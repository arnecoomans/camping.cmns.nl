from django.views.generic import View, UpdateView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.text import slugify
#from django.db.models import BooleanField, ManyToManyField

#from django.contrib.auth.models import User

# from location.models.Location import Location, Category, Chain
from location.models.Profile import Profile, VisitedIn
from location.models.Tag import Tag
from location.models.Comment import Comment
from location.models.Media import Media
from .json.jsonhelper import JSONHelper
# from location.models.Media import Media

''' Toggle View
    - Toggle a value for a specific object
    The view requires:
    @param model: Model to be toggled
    @param field: Field to be toggled
    @param value: Value to be toggled (optional)
    - Format: /json/<model>:<(slug)>/<field>/<(value)>/
    - Example: /json/profile/maps-permission/ (No slug, no value)
    - Example: /json/location:domaine-les-gandins/like/ (No value)
    - Example: /json/location:domaine-les-gandins/category/restaurant/
'''
class ToggleAttribute(JSONHelper):
  
  ''' Toggle Functions '''
  def __toggleBoolean(self, field):
    try:
      setattr(self.get_object(), self.get_field(), not self.get_current_value())
      self.get_object().save()
      self.messages.append(('success', f"{ _('toggled {} to {}').format(self.__get_field_display(), getattr(self.get_object(), self.get_field())).capitalize() } { self.get_undo_link() }"))
    except Exception as e:
      self.status = 500
      self.messages.append(('danger', f"[137] { _('error when toggling {} of {}: {}').format(self.get_field(), self.get_object(), escape(e)).capitalize()}"))

  def __toggleForeignKey(self, field):
    ''' Fetch textual Value - should be slug of the object '''
    value = self.get_value()
    if not value:
      self.status = 500
      self.messages.append(('danger', f"[181] { _('value is required but missing').capitalize() }"))
      return False
    ''' Get the model of the ForeignKey '''
    value_model = self.get_model()._meta.get_field(self.get_field()).related_model
    ''' Get the value object '''
    try:
      object = value_model.objects.get(slug=value)
    except value_model.DoesNotExist:
      self.status = 404
      self.messages.append(('danger', f"[404] { _('value "{}" not found').format(value).capitalize() }"))
      return False
    ''' Toggle the value '''
    if getattr(self.get_object(), self.get_field()) == object:
      ''' Value is already set: Remove it '''
      setattr(self.get_object(), self.get_field(), None)
      self.messages.append(('success', f"{ _('removed {} from {}').format(object, self.get_field()).capitalize() } { self.get_undo_link() }"))
    else:
      ''' Value should be set '''
      setattr(self.get_object(), self.get_field(), object)
      self.messages.append(('success', f"{ _('set {} to {}').format(self.get_field(), object).capitalize() } { self.get_undo_link() }"))
    self.get_object().save()


  def __toggleManyToMany(self, field):
    ''' Fetch textual Value - should be slug of the object '''
    value = self.get_value()
    if not value:
      self.status = 500
      self.messages.append(('danger', f"[181] { _('value is required but missing').capitalize() }"))
      return False
    ''' Get the model of the ManyToManyField '''
    value_model = self.get_model()._meta.get_field(self.get_field()).related_model
    ''' Handle parent/child relations '''
    if self.parent:
      defaults = { 'name': self.parent.replace('-', ' ').title(), 'user': self.request.user }
      parent = value_model.objects.get_or_create(slug=slugify(self.parent.lower()), defaults={ 'name': self.parent.capitalize(), 'user': self.request.user })
      if parent[1]:
        self.messages.append(('info', f"{ _('parent {} {} created').format(value_model.__name__, parent[0].name).capitalize() }"))
      parent = parent[0]
    else:
      parent = None
    ''' Get or Create the value object '''
    defaults = { 'name': self.get_value_display(), 'user': self.request.user }
    if 'parent' in [field.name for field in value_model._meta.get_fields()]:
      defaults['parent'] = parent
    if 'slug' in [field.name for field in value_model._meta.get_fields()]:
      value_object = value_model.objects.get_or_create(slug=slugify(value.lower()), defaults=defaults)
    elif 'username' in [field.name for field in value_model._meta.get_fields()]:
      value_object = value_model.objects.get_or_create(username=value.lower(), defaults=defaults)
    elif self.get_field() == 'link':
      try:
        value_object = (value_model.objects.get(id=value), False)
      except ValueError:
        defaults['name'] = ''
        value_object = value_model.objects.get_or_create(url=value.lower(), defaults=defaults)
        self.value = value_object[0].id
      except value_model.DoesNotExist:
        self.status = 404
        self.messages.append(('danger', f"[404] { _('value "{}" not found').format(value).capitalize() }"))
        return self.return_response()
    else:
      self.status = 500
      self.messages.append(('danger', f"[520s] { _('lookup for model "{}" not supported in {}: {}').format(value_model.__name__, self.get_model().__name__, value_model._meta.get_fields()).capitalize() }"))
      return self.return_response()
    if value_object[1]:
      self.messages.append(('info', f"{ _('{} {} created').format(value_model.__name__, value_object[0].name).capitalize() }"))
    value_object = value_object[0]
    ''' Toggle the value '''
    if value_object in getattr(self.get_object(), self.get_field()).all():
      ''' Value is already in the ManyToManyField: Remove it '''
      getattr(self.get_object(), self.get_field()).remove(value_object)
      value_object_name = (
        value_object.name if hasattr(value_object, 'name') and value_object.name 
        else value_object.get_title() if hasattr(value_object, 'get_title') 
        else value_object.username
      )
      self.messages.append(('success', f"{ _('removed "{}" from {} {}').format(value_object_name, self.get_field(), self.get_object().name).capitalize() } { self.get_undo_link() }"))
    else:
      ''' Value should be added '''
      try:
        getattr(self.get_object(), self.get_field()).add(value_object)
        value_object_name = (
          value_object.name if hasattr(value_object, 'name') and value_object.name 
          else value_object.get_title() if hasattr(value_object, 'get_title') 
          else value_object.username
        )
        self.messages.append(('success', f"{ _('added "{}" to {} {}').format(value_object_name, self.get_field(), self.get_object()).capitalize() } { self.get_undo_link() }"))
      except Exception as e:
        self.status = 500
        self.messages.append(('danger', f"[152] { _('Error when adding {} to {} of {}: {}').format(value, self.get_field(), self.get_object(), escape(e)) }"))
  
  ''' Get function 
      @scope: public
      @param request: request object
      @return: JsonResponse
      - Get the object that needs a value toggled
      - Toggle the value of the object
      - Return a JSON response with the status and messages
  '''
  def get(self, request, *args, **kwargs):
    ''' Check if user is authenticated '''
    if not request.user.is_authenticated:
      self.status = 401
      self.messages.append(('danger', f"[401] { _('user is not authenticated').capitalize() }"))
      return self.return_response()
    ''' Get Field 
        Field Access the Object in the Model
    '''
    field = self.get_field()
    ''' Verify Progress '''
    if field: 
      field_type =  self.get_model()._meta.get_field(self.get_arg('field')).__class__.__name__
      ''' Based on Field Type, toggle the value '''
      if field_type == 'BooleanField':
        self.__toggleBoolean(field)
      elif field_type == 'ForeignKey':
        self.__toggleForeignKey(field)
      elif field_type == 'ManyToManyField':
        self.__toggleManyToMany(field)
      else:
        self.messages.append(('danger', f"[192] { _('Field "{}" with type "{}" not supported for model "{}"').format(field, field_type, self.get_model().__name__) }"))
    ''' Return response '''
    return self.return_response()


''' Toggle Exceptions '''
class ToggleDeleted(UpdateView):
  # /toggle/<model>/<pk>/delete/ or /toggle/<model>/<slug>/delete/
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.model = None
    self.object = None
    self.kwargs = kwargs
    self.success_url = None
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
      'media': {
        'model': Media,
        'success_url': 'location:MediaStack',
        'ajax_success_url': 'location:getAttributesFor',
      }
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
          object = self.get_model().objects.get(slug=self.kwargs['slug'])
        else:
          object = self.get_model().objects.get(pk=self.kwargs['pk'])
        self.object = object
      else:
        self.object = None
    return self.object
  
  def get_success_url(self):
    if self.success_url:
      return redirect(self.success_url)
    elif self.models[self.kwargs['model'].lower().strip()]['success_url']:
      if hasattr(self.get_object(), 'location'):
        self.success_url = redirect(self.models[self.kwargs['model'].lower().strip()]['success_url'], self.get_object().location.slug)
      else:
        self.success_url = redirect(self.models[self.kwargs['model'].lower().strip()]['success_url'])
    return self.success_url
  
  def get_ajax_success_url(self):
    if self.success_url:
      return redirect(self.success_url)
    elif self.models[self.kwargs['model'].lower().strip()]['ajax_success_url']:
      if hasattr(self.get_object(), 'location'):
        self.success_url = reverse_lazy(self.models[self.kwargs['model'].lower().strip()]['ajax_success_url'], kwargs={'location': self.get_object().location.slug, 'attribute': 'comment'})
      else:
        self.success_url = reverse_lazy(self.models[self.kwargs['model'].lower().strip()]['ajax_success_url'])
    return self.success_url
  
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
    if 'slug' in [field.name for field in self.get_model()._meta.get_fields()]:
      url = reverse_lazy("location:ToggleDeletedBySlug", kwargs={"model": self.kwargs['model'], "slug": self.kwargs['slug']})
    else:
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