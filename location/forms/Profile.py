# forms.py
from django import forms
from ..models import Profile, NavigationApps

class ProfileForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = "__all__"

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not self.instance.pk:  # enkel bij nieuw object
      self.fields["navigationapps"].initial = NavigationApps.objects.filter(default_enabled=True)
