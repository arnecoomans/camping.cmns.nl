from typing import Any
from django.db import models
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.shortcuts import redirect


from django.utils.translation import gettext as _

from location.models.Profile import Profile
from location.models.Location import Location

class ProfileView(UpdateView):
  fields = ['home']

  def get_object(self):
    if not hasattr(self.request.user, 'profile'):
      profile = Profile.objects.create(user=self.request.user)
      messages.add_message(self.request, messages.INFO, f"{ _('created profile for ') } { self.request.user.get_full_name() }")
    return self.request.user.profile 
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # profile = SE
    context['profile'] = self.get_object()
    context['homes'] = Location.objects.filter(category__slug='home', user=self.request.user)
    context['available_family'] = User.objects.exclude(id__in=self.get_object().family.all()).exclude(id=self.request.user.id)
    context['scope'] = f"{ _('profile') }: { _('edit your profile') }"
    return context
  
    return form
  def form_invalid(self, form):
    messages.add_message(self.request, messages.WARNING, f"{ _('Form cannot be saved because of the following error(s)') }: { form.errors }")
    return super().form_invalid(form)
  
  def form_valid(self, form):
    ''' See if User Data has changed '''
    user = User.objects.get(id=self.get_object().user.id)
    changes = 0
    for field in ['first_name', 'last_name', 'email']:
      if self.request.POST.get(field, '') != getattr(user, field):
        setattr(user, field, self.request.POST.get(field, ''))
        changes += 1
    if user.email != user.username:
      messages.add_message(self.request, messages.INFO, f"{ _('Your email address has changed') }. { _('This means your username has changed as well') }.")
    if changes > 1:
      user.save()
    ''' Non-user changes are handled by class and should be handled without other care '''
    messages.add_message(self.request, messages.SUCCESS, f"{ _('Your changes have been saved') }.")
    return super().form_valid(form)
  

''' Toggle Favorite '''
class ToggleFavoriteLocation(UpdateView):
  model = Location
  fields = ['slug']

  def get(self, request, *args, **kwargs):
    location = Location.objects.get(slug=kwargs['slug'])
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
  


''' Sign up '''
class SignUpView(CreateView):
  model = User
  #form_class = UserCreationForm
  success_url = reverse_lazy('location:register')
  template_name = 'registration/user_register_form.html'
  fields = ['password', 'first_name', 'last_name', 'email']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['register'] = True
    return context
  
  def form_invalid(self, form):
    messages.add_message(self.request, messages.INFO, 'invalid form: ' + str(form.errors))
    return super().form_invalid(form)

  def form_valid(self, form):
    ''' Process form input '''
    username = form.cleaned_data['email'].lower()
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']
    ''' Username validation 
        Username and e-mail should be unique. In rare cases that username is not the same as e-mail 
        (legacy users, superuser), avoid that the email is re-used for registering an account.
    '''
    objects = User.objects.filter(username=username) | User.objects.filter(email=email)
    if objects.count() > 0:
      messages.add_message(self.request, messages.ERROR, f"{ _('Error when registering') }:<br>{ _('Username or e-mail is already registered') }. { _('You can') } <a href=\"{ reverse_lazy('login') }\">{ _('log in here') }</a>.")
      return redirect(reverse_lazy('location:register'))  
    ''' Password validation '''
    try:
      validate_password(password, user=username)
    except ValidationError as e:
      messages.add_message(self.request, messages.ERROR, f"{ _('Your password does not meet the requirements') }:<br> { '.<br>'.join(e) }")
      return redirect(reverse_lazy('location:register'))  
    if username.lower() == password.lower() or password.lower() in username.lower() or username.lower() in password.lower():
      messages.add_message(self.request, messages.ERROR, f"{ _('Your password does not meet the requirements') }:<br> { _('The password cannot overlap with the username') }.")
      
      return redirect(reverse_lazy('location:register'))  
    ''' Create new user '''
    user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
    user.save()
    messages.add_message(self.request, messages.SUCCESS, _('Succesfully registered your account. Please log in with your e-mail address and chosen password. '))
    ''' Set default groups '''
    if hasattr(settings, 'NEW_USER_DEFAULT_GROUP'):
      group = Group.objects.get_or_create(name=settings.NEW_USER_DEFAULT_GROUP)[0]
      group.user_set.add(user)
    ''' Redirect to login page '''
    return redirect(reverse_lazy('location:home'))
