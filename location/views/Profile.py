from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.shortcuts import redirect

from .func_filter_status import filter_status
from .func_filter_visibility import filter_visibility


from django.utils.translation import gettext as _

from location.models.Profile import Profile
from location.models.Location import Location

class ProfileView(UpdateView):
  fields = ['home', 'hide_least_liked']

  def get_object(self):
    if not hasattr(self.request.user, 'profile'):
      profile = Profile.objects.create(user=self.request.user)
      messages.add_message(self.request, messages.INFO, f"{ _('created profile for ') } { profile.user.get_full_name() }")
    return self.request.user.profile 
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['profile'] = self.get_object()
    homes = Location.objects.filter(category__slug='home')
    homes = filter_status(self.request.user, homes)
    homes = filter_visibility(self.request.user, homes)
    homes = homes.order_by().distinct
    context['homes'] = homes
    context['available_family'] = User.objects.exclude(id__in=self.get_object().family.all()).exclude(id=self.request.user.id)
    context['scope'] = f"{ _('profile') }: { _('edit your profile') }"
    return context
  
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
    if changes > 1:
      ''' If changes have been made to the user, save the user object '''
      user.save()
    ''' Non-user changes are handled by class and should be handled without other care '''
    messages.add_message(self.request, messages.SUCCESS, f"{ _('Your changes have been saved') }.")
    return super().form_valid(form)
  





''' Sign up '''
class SignUpView(CreateView):
  model = User
  #form_class = UserCreationForm
  success_url = reverse_lazy('location:register')
  template_name = 'registration/user_register_form.html'
  fields = ['password', 'first_name', 'last_name', 'email', 'username']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['register'] = True
    return context
  
  def form_invalid(self, form):
    messages.add_message(self.request, messages.INFO, 'invalid form: ' + str(form.errors))
    return super().form_invalid(form)

  def form_valid(self, form):
    ''' Process form input '''
    username = form.cleaned_data['username']
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
    messages.add_message(self.request, messages.SUCCESS, _('Succesfully registered your account. Please log in with your username and chosen password.'))
    ''' Set default groups '''
    if hasattr(settings, 'NEW_USER_DEFAULT_GROUP'):
      group = Group.objects.get_or_create(name=settings.NEW_USER_DEFAULT_GROUP)[0]
      group.user_set.add(user)
    ''' Redirect to login page '''
    return redirect(reverse_lazy('login'))
