from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.urls import reverse_lazy


from location.models.Location import Location, Category, Chain
from location.models.Profile import Profile, VisitedIn
from location.models.Tag import Tag
from location.models.Comment import Comment


class JSONHelper(View):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.model = None
    self.object = None
    self.slug = None
    self.field = None
    self.value = None
    self.parent = None
    self.status = 200
    self.messages = []
    self.models = {
      'tag': Tag,
      'category': Category,
      'chain': Chain,
      'location': Location,
      'profile': Profile,
    }

  ''' Get Value from URL
      @scope: private
      @param key: key to be fetched from URL
      @return: value from URL
      Retrieves the parameter from URL, POST or GET request
  '''
  def get_value_from_url(self, key):
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
      get_value_from_url if not found
  '''
  def get_arg(self, key):
    if getattr(self, key) == None:
      ''' Cache is not yet filled, fetch value from URL '''
      setattr(self, key, self.get_value_from_url(key))
    return getattr(self, key)
  
  ''' Get Model
      @scope: private
      @return: Model that holds the object that needs a value toggled
  '''
  def get_model(self):
    if self.model == None:
      ''' Fetch Model Name from URL, GET or POST '''
      model = self.get_value_from_url('model')
      ''' Verify if model is supported '''
      if model in self.models:
        ''' Model is supported, store reference to Model '''
        self.model = self.models[model]
      else:
        self.status = 500
        self.messages.append(('danger', f"[122] { _('model "{}" not supported').format(model.__name__).capitalize }"))
        self.model = False
    return self.model
  
  def get_object(self):
    if self.object == None:
      ''' Fetch Model '''
      model = self.get_model()
      ''' Set Object if Slug is supplied'''
      if self.get_slug():
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
            self.object = model.objects.get(user__username__iexact=self.get_slug())
          except model.DoesNotExist:
            self.status = 404
            self.messages.append(('danger', f"[286] { _('model "{}" requires user but no object found for user {}').format(model.__name__, self.get_slug()).capitalize() }"))
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

  def get_slug(self):
    return self.get_arg('slug')
  
  def get_field(self):
    if self.field == None:
      field = self.get_arg('field')
      if field in [field.name for field in self.get_model()._meta.get_fields()]:
        self.field = field
      else:
        self.status = 500
        self.messages.append(('danger', f"[127] { _('field "{}" not supported for model "{}"').format(field, self.get_model().__name__).capitalize() }"))
        self.field = False
    return self.field
  
  def __get_field_display(self):
    return self.get_field().replace('_', ' ').capitalize()

  def get_value(self):
    if self.value == None:
      if self.get_arg('value'):
        ''' Detect parent but not for URL's '''
        if ':' in self.get_arg('value') and not '://' in self.get_arg('value'):
          self.parent =self.get_arg('value').split(':')[0] 
          self.value = '-'.join(self.get_arg('value').split(':')[1:])
        else:
          self.value = self.get_arg('value')
      else:
        self.value = False
    return self.value
  
  def get_value_display(self):
    return self.get_value().replace('-', ' ').title()
  
  def get_current_value(self):
    return getattr(self.get_object(), self.get_field())
  
  def return_response(self):
    field = self.get_field()
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
      'undo-url': self.get_undo_url(),
      'field': str(field) + 'list',
    }
    return JsonResponse(response, status=self.status)

  def get_undo_url(self):
    resolver = self.request.resolver_match.url_name
    kwargs = {
      'model': self.get_model().__name__.lower(),
    }
    if self.get_field():
      kwargs['field'] = self.get_field()
    if self.get_object() and 'slug' in self.get_object()._meta.get_fields():
      kwargs['slug'] = self.get_object().slug
    if 'slug' in resolver.lower():
      kwargs['slug'] = self.get_slug()
    if self.get_value():
      resolver += 'WithValue' if 'WithValue' not in resolver else ''
      kwargs['value'] = self.get_value()
    return reverse_lazy("location:" + resolver, kwargs=kwargs)
  
  def get_undo_link(self):
    return f'(<a href="{ self.get_undo_url() }" class="toggable">{ _('undo').capitalize() })</a>'