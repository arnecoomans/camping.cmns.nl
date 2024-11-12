from django.views.generic import View, UpdateView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils.html import escape
from django.utils.text import slugify
from django.db.models import BooleanField, ManyToManyField

from django.contrib.auth.models import User

from location.models.Location import Location, Category, Chain
from location.models.Profile import Profile, VisitedIn
from location.models.Tag import Tag
from location.models.Comment import Comment
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
class ToggleAttribute(View):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.model = None
    self.object = None
    self.slug = None
    self.field = None
    self.value = None
    self.parent = None

    self.models = {
      'tag': Tag,
      'category': Category,
      'chain': Chain,
      'location': Location,
      'profile': Profile,
    }
    self.status = 200
    self.messages = []

  ''' Get Value from URL
      @scope: private
      @param key: key to be fetched from URL
      @return: value from URL
      Retrieves the parameter from URL, POST or GET request
  '''
  def __get_value_from_url(self, key):
    if key in self.kwargs:
      ''' Key is in URL '''
      return self.kwargs[key]
    elif self.request.GET.get(key, False):
      ''' Key is in GET request '''
      return self.request.GET.get(key)
    elif self.request.POST.get(key, False):
      ''' Key is in POST request '''
      return self.request.POST.get(key)
    else:
      ''' Key is not found'''
      return False
  
  ''' Get Argument From Class Cache
      @scope: private
      @param key: key to be fetched from Class Cache
      @return: value from Class Cache
      Retrieves the parameter from class cache, falls back to 
      __get_value_from_url if not found
  '''
  def __get_arg(self, key):
    if getattr(self, key) == None:
      ''' Cache is not yet filled, fetch value from URL '''
      setattr(self, key, self.__get_value_from_url(key))
    return getattr(self, key)
  
  ''' Get Model
      @scope: private
      @return: Model that holds the object that needs a value toggled
  '''
  def __get_model(self):
    if self.model == None:
      ''' Fetch Model Name from URL, GET or POST '''
      model = self.__get_value_from_url('model')
      ''' Verify if model is supported '''
      if model in self.models:
        ''' Model is supported, store reference to Model '''
        self.model = self.models[model]
      else:
        self.status = 500
        self.messages.append(('danger', f"[122] { _('model "{}" not supported').format(model.__name__).capitalize }"))
        self.model = False
    return self.model
  
  def __get_object(self):
    if self.object == None:
      ''' Fetch Model '''
      model = self.__get_model()
      ''' Set Object if Slug is supplied'''
      if self.__get_slug():
        ''' Select Object within Model By Slug'''
        if 'slug' in [field.name for field in model._meta.get_fields()]:
          ''' Model has Slug Field, get object by slug '''
          try:
            self.object = model.objects.get(slug__iexact=self.slug)
          except model.DoesNotExist:
            self.status = 404
            self.messages.append(('danger', f"[282] { _('model "{}" requires slug but no object found with slug {}').format(model.__name__, self.slug).capitalize() }"))
            self.object = False
        elif 'user' in [field.name for field in model._meta.get_fields()]:
          ''' Model has User Field (example: profile), get or create object where user = current user '''
          try:
            # @TODO: Check if user is authenticated
            self.object = model.objects.get(user__username__iexact=self.__get_slug())
          except model.DoesNotExist:
            self.status = 404
            self.messages.append(('danger', f"[286] { _('model "{}" requires user but no object found for user {}').format(model.__name__, self.__get_slug()).capitalize() }"))
            self.object = False
        else:
          ''' Lookup field not available in Model, log an error message '''
          self.status = 500
          self.messages.append(('danger', f"[854] { _('lookup for model "{}" not supported').format(model.__name__).capitalize() }"))
          self.object = False
      else:
        ''' No Slug supplied, fall back to defaults '''
        if 'user' in [field.name for field in model._meta.get_fields()]:
          ''' If Model has User Field (example: profile), get or create object where user = current user '''
          try:
            self.object = model.objects.get_or_create(user=self.request.user)[0]
          except model.DoesNotExist:
            self.status = 404
            self.messages.append(('danger', f"[284] { _('model "{}" requires user but no object found for user {}').format(model.__name__, self.request.user).capitalize() }"))
            self.object = False
    return self.object
  
  def __get_slug(self):
    return self.__get_arg('slug')

  def __get_field(self):
    if self.field == None:
      field = self.__get_arg('field')
      if field in [field.name for field in self.__get_model()._meta.get_fields()]:
        self.field = field
      else:
        self.status = 500
        self.messages.append(('danger', f"[127] { _('field "{}" not supported for model "{}"').format(field, self.__get_model().__name__).capitalize() }"))
        self.field = False
    return self.field
  
  def __get_field_display(self):
    return self.__get_field().replace('_', ' ').capitalize()

  def __get_value(self):
    if self.value == None:
      if self.__get_arg('value'):
        if ':' in self.__get_arg('value'):
          self.parent =self.__get_arg('value').split(':')[0] 
          self.value = '-'.join(self.__get_arg('value').split(':')[1:])
        else:
          self.value = self.__get_arg('value')
      else:
        self.value = False
    return self.value
  
  def __get_value_display(self):
    return self.__get_value().replace('-', ' ').title()
  
  def __get_current_value(self):
    return getattr(self.__get_object(), self.__get_field())
  
  ''' Toggle Functions '''
  def __toggleBoolean(self, field):
    try:
      setattr(self.__get_object(), self.__get_field(), not self.__get_current_value())
      self.__get_object().save()
      self.messages.append(('success', f"{ _('toggled {} to {}').format(self.__get_field_display(), getattr(self.__get_object(), self.__get_field())).capitalize() } { self.__get_undo_link() }"))
    except Exception as e:
      self.status = 500
      self.messages.append(('danger', f"[137] { _('error when toggling {} of {}: {}').format(self.__get_field(), self.__get_object(), escape(e)).capitalize()}"))

  def __toggleManyToMany(self, field):
    ''' Fetch textual Value - should be slug of the object '''
    value = self.__get_value()
    if not value:
      self.status = 500
      self.messages.append(('danger', f"[181] { _('value is required but missing').capitalize() }"))
      return False
    ''' Get the model of the ManyToManyField '''
    value_model = self.__get_model()._meta.get_field(self.__get_field()).related_model
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
    defaults = { 'name': self.__get_value_display(), 'user': self.request.user, 'parent': parent }
    value_object = value_model.objects.get_or_create(slug=slugify(value.lower()), defaults=defaults)
    if value_object[1]:
      self.messages.append(('info', f"{ _('{} {} created').format(value_model.__name__, value_object[0].name).capitalize() }"))
    value_object = value_object[0]
    ''' Toggle the value '''
    if value_object in getattr(self.__get_object(), self.__get_field()).all():
      ''' Value is already in the ManyToManyField: Remove it '''
      getattr(self.__get_object(), self.__get_field()).remove(value_object)
      self.messages.append(('success', f"{ _('removed {} from {} {}').format(value_object.name, self.__get_field(), self.__get_object().name).capitalize() } { self.__get_undo_link() }"))
    else:
      ''' Value should be added '''
      try:
        getattr(self.__get_object(), self.__get_field()).add(value_object)
        self.messages.append(('success', f"{ _('added {} to {} {}').format(value, self.__get_field(), self.__get_object()).capitalize() } { self.__get_undo_link() }"))
      except Exception as e:
        self.status = 500
        self.messages.append(('danger', f"[152] { _('Error when adding {} to {} of {}: {}').format(value, self.__get_field(), self.__get_object(), escape(e)) }"))


  def __get_undo_url(self):
    resolver = self.request.resolver_match.url_name
    kwargs = {
      'model': self.__get_model().__name__.lower(),
      'field': self.__get_field(),
    }
    if 'slug' in resolver.lower():
      kwargs['slug'] = self.__get_slug()
    if self.__get_value():
      resolver += 'WithValue' if 'WithValue' not in resolver else ''
      kwargs['value'] = self.__get_value()
    return reverse_lazy("location:" + resolver, kwargs=kwargs)
  
  def __get_undo_link(self):
    return f'(<a href="{ self.__get_undo_url() }" class="toggable">{ _('undo').capitalize() })</a>'
  
  def __return_response(self):
    field = self.__get_field()
    if field in ['favorite', 'dislike', 'ignored_tags']:
      field = 'action'
    response = {
      '__meta': {
        'url': self.request.path,
        'resolver': self.request.resolver_match.url_name,
        'user': self.request.user.username if self.request.user.is_authenticated else False,
      },
      'status': self.status,
      'messages': self.messages,
      'undo-url': self.__get_undo_url(),
      'field': str(field) + 'list',
    }
    return JsonResponse(response, status=self.status)
  
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
      return self.__return_response()
    ''' Get Field 
        Field Access the Object in the Model
    '''
    field = self.__get_field()
    ''' Verify Progress '''
    if field: 
      field_type =  self.__get_model()._meta.get_field(self.__get_arg('field')).__class__.__name__
      ''' Based on Field Type, toggle the value '''
      if field_type == 'BooleanField':
        self.__toggleBoolean(field)
      elif field_type == 'ManyToManyField':
        self.__toggleManyToMany(field)
      else:
        self.messages.append(('danger', f"[192] { _('Field "{}" with type "{}" not supported for model "{}"').format(field, field_type, self.__get_model().__name__) }"))
    ''' Return response '''
    return self.__return_response()


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