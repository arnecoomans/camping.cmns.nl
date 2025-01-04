from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import redirect, reverse
from django.conf import settings

from datetime import datetime
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener

''' Required for streaming downloads to user '''
from django_sendfile import sendfile
from django.http import Http404
from django.core.exceptions import PermissionDenied

from pathlib import Path

from .snippets.filter_class import FilterClass
from .snippets.order_media import order_media

from location.models.Media import Media
from location.models.Location import Location

class AddMediaToLocation(CreateView):
  model = Media
  fields = ['source', 'title', 'location', 'visibility']

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('media') }: { _('add media') }"
    context['location'] = Location.objects.get(slug=self.kwargs['slug'])
    return context
  
  def post(self, request, *args, **kwargs):
    ''' Check uploaded file '''
    if len(self.request.FILES) != 1:
      messages.add_message(self.request, messages.INFO,
                           f"{ _('the form cannot be processed: too little or too many files selected') }.")
      return redirect('location:AddMediaToLocation', self.kwargs['slug'])
    ''' Get Uploaded File Info '''
    original_filename = Path(str(self.request.FILES['source']))
    ''' Check extention of file if it can be processed and set the new filename '''
    if original_filename.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.heic']:
      ''' New filename format is YYYY-MM-DD-[original filename].[orignial suffix] '''
      target_filename = Path(datetime.now().strftime("%Y-%m-%d-") + str(original_filename))
    else:
      ''' If the file is of unsupported extention, stop processing '''
      messages.add_message(self.request, messages.INFO,
                           "Unsupported File Type")
      return redirect('location:AddMediaToLocation', self.kwargs['slug'])
    heic = False
    if original_filename.suffix.lower() == '.heic':
      ''' If a .heic is detected, load heif-opener and add format to target file '''
      register_heif_opener()
      heic = True
      target_filename = target_filename.with_suffix('.jpg')
      messages.add_message(self.request, messages.INFO,
                           f"{ _('detected .heic-image, converting to jpeg') }.")
    ''' Do Sanity Check
        - Target Image should not exist
        - if it does exist, add a number behind the image name
    '''
    if settings.MEDIA_ROOT.joinpath(target_filename).exists():
      messages.add_message(self.request, messages.WARNING, f"{ _('file already exists, selecting a different filename') }.")
      i = 1
      while settings.MEDIA_ROOT.joinpath(target_filename).with_name(f"{ target_filename.stem }-{ str(i) }") .exists():
        i += 1
      target_filename = target_filename.with_name(f"{ target_filename.stem }-{ str(i) }").with_suffix(target_filename.suffix)
    ''' Force Title '''
    title = self.request.POST.get('title', '')
    title = target_filename.name if len(title) == 0 else title
    ''' Force User '''
    user = self.request.user
    visibility = self.request.POST.get('visibility', 'c')
    location = Location.objects.get(slug=self.request.POST.get('location', ''))
    ''' Store Image to Filesystem '''
    original_image = self.request.FILES['source']
    tgt_width = 2048
    with Image.open(original_image) as image:
      ''' If image is wider than 2048 px, resize the image to 2048px'''
      width, height = image.size
      if width > tgt_width:
        messages.add_message(self.request, messages.INFO,
                             f"{ _('detected large image, resizing to maximum of') } { str(tgt_width) } pixels.")
        ratio = width / height
        tgt_height = int(tgt_width / ratio)
        image = image.resize((tgt_width, tgt_height),
                             Image.Resampling.LANCZOS)
      elif width > tgt_width / 2:
        messages.add_message(self.request, messages.WARNING, f"{ _('the resolution of the uploaded image is very low') }. { _('You might want to concider using a high resulution image') }.")
      if heic:
        image = image.save(settings.MEDIA_ROOT / target_filename,
                            format="JPEG")
      else:
        image = image.save(settings.MEDIA_ROOT / target_filename)
    ''' Store Media Object '''
    media = Media.objects.update_or_create(location=location, 
                                           source=str(target_filename),
                                           defaults={
                                             'title': title,
                                             'visibility': visibility,
                                             'user': user,
                                           })
    ''' File uploaded and reference stored in database '''
    messages.add_message(self.request, messages.SUCCESS,
                         f"{ _('succesfully added image') } { target_filename.name } { _('to') } { location.name }.")
    return redirect(self.get_success_url())

  def get_success_url(self) -> str:
    return reverse('location:location', kwargs={'slug': self.kwargs['slug']})

class MediaRefreshView(UpdateView):
  model = Media
  fields = ['date_updated']

  def get(self, *args, **kwargs):
    messages.add_message(self.request, messages.SUCCESS, f"{ _('updated timestamp for image') } { self.get_object().title } { _('and moved up in ordering') }.")
    self.get_object().save()
    return redirect('location:MediaStack', self.get_object().location.slug)
  
class StackView(FilterClass, ListView):
  model = Media

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('media') }: { _('list media') }"
    context['location'] = Location.objects.get(slug=self.kwargs['slug'])
    context['media'] = order_media(self.get_queryset())
    return context
  
  def get_queryset(self):
    queryset = Media.objects.filter(location__slug=self.kwargs['slug'])
    queryset = self.filter_status(queryset)
    queryset = self.filter_visibility(queryset)
    return queryset
  
class MediaStreamView(DetailView, FilterClass):
  model = Media

  def __get_object(self):
    ''' Get filename from URL '''
    filename = self.kwargs['filename']
    ''' Verify if file exists in /public/media/ '''
    media = settings.MEDIA_ROOT.joinpath(filename)
    if not media.exists():
      ''' If file does not exist, return 404 '''
      raise Http404
    return media

  def get(self, request, *arg, **kwargs):
    ''' Fetch Media Object '''
    file = self.__get_object()
    ''' Verify if file is accessible by the current user '''
    try:
      media = Media.objects.get(source=file.name)
    except Media.DoesNotExist:
      ''' If media object does not exist, return 404 '''
      raise Http404
    ''' Check if the media object is visible 
        P - Publicly visible
        C - Community Visible
        F - Family Visible
        Q - Private
    '''
    if media.visibility == 'p':
      ''' If media object is public, return the file '''
      return sendfile(request, file)
    ''' For all other visibility settings, check if the user is authenticated '''
    if not request.user.is_authenticated:
      ''' If user is not authenticated, return 403 '''
      raise PermissionDenied
    ''' If media object is community visible, return the file '''
    if media.visibility == 'c':
      return sendfile(request, file)
    ''' For Private visibility, check if the user is the owner '''
    if media.visibility == 'q':
      if media.user == request.user:
        ''' If user is the owner, return the file '''
        return sendfile(request, file)
      ''' If user is not the owner, return 403 '''
      raise PermissionDenied
    if media.visibility == 'f':
      ''' If media user is request user, show the file '''
      if media.user == request.user:
        return sendfile(request, file)
      ''' If user is not the owner, check if user is in the same family '''
      if hasattr(media.user, 'profile') and request.user in media.user.profile.family.all():
        ''' If user is in the same family, show the file '''
        return sendfile(request, file)
      ''' If user is not in the same family, return 403 '''
      raise PermissionDenied
    

    
    ''' If media object is visible, return the file '''
    return sendfile(request, file)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['scope'] = f"{ _('media') }: { self.object.title }"
    return context