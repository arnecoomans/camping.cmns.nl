from django.contrib import admin
from django.contrib import messages

from .models import *


''' Default Model Admin Class Templates '''
class DefaultAdmin(admin.ModelAdmin):
  def get_changeform_initial_data(self, request):
    get_data = super(DefaultAdmin, self).get_changeform_initial_data(request)
    get_data['user'] = request.user.pk
    return get_data

class SlugDefaultAdmin(DefaultAdmin):
  prepopulated_fields = {'slug': ('name',)}
  list_display = ['name', 'slug']

  def get_list_display(self, request):
    # Start with the base list_display
    list_display = list(self.list_display)
    # Check if the model has a "parent" field
    if hasattr(self.model, 'parent'):
      list_display.append('parent')
    return list_display
  
''' ReadOnlyAdmin
    * Set all fields in admin to read-only
    * Disallow permission to add new record
    * Disallow permission to delete record
'''
class ReadOnlyAdmin(admin.ModelAdmin):
  readonly_fields = []
  def get_readonly_fields(self, request, obj=None):
    return list(self.readonly_fields) + \
      [field.name for field in obj._meta.fields] + \
      [field.name for field in obj._meta.many_to_many]


  def has_add_permission(self, request):
    return False

  def has_delete_permission(self, request, obj=None):
    return False

''' Admin Tasks '''
''' Admin Tasks for Locations '''
@admin.action(description='Get address of location based on name')
def getAddress(modeladmin, request, queryset):
  for location in queryset:
    location.getAddress(request)
@admin.action(description='Get lat and lng of location')
def getLatLng(modeladmin, request, queryset):
  for location in queryset:
    location.getLatLng(request)
@admin.action(description='Get distance from departure center')
def getDistanceFromDepartureCenter(modeladmin, request, queryset):
  for location in queryset:
    location.getDistanceFromDepartureCenter(request)
@admin.action(description='Store region for location')
def getRegion(modeladmin, request, queryset):
  for location in queryset:
    location.getRegion(request)
@admin.action(description='clear cachable data')
def clearCachableData(modeladmin, request, queryset):
  for location in queryset:
    location.address = ''
    location.coord_lat = ''
    location.coord_lng = ''
    location.distance_to_departure_center = None
    location.save()
    messages.add_message(request, messages.INFO, 'Reset cachable fields for location')
@admin.action(description='generate thumbnail')
def GenerateThumbnail(modeladmin, request, queryset):
  for image in queryset:
    image.GenerateThumbnail(request)
@admin.action(description='Get API Data')
def getData(modeladmin, request, queryset):
  for record in queryset:
    record.getData(request)
@admin.action(description='Migrate website to link')
def migrateWebsiteToLink(modeladmin, request, queryset):
  for record in queryset:
    link = Link.objects.get_or_create(url=record.website, defaults={'primary':True, 'user':request.user, 'visibility':'p'})[0]
    record.link.add(link)
    messages.add_message(request, messages.INFO, f"Migrated website { record.website } to link { link.id } for { record.name }")
@admin.action(description='Copy Description to Descriotions')
def copyDescriptionToDescriptions(modeladmin, request, queryset):
  for location in queryset:
    if len(location.description.strip()) > 0:
      object = Description.objects.create(description=location.description, user=request.user)
      location.descriptions.add(object)
      messages.add_message(request, messages.INFO, f"Description copied to Descriptions for { location.name }")

''' Custom Model Admin Classes '''
class LocationAdmin(SlugDefaultAdmin):
  actions = [getAddress, getLatLng, getDistanceFromDepartureCenter, getRegion, clearCachableData, copyDescriptionToDescriptions]
  list_display = ['name', 'location', 'status']
  list_filter = ['status', 'chain']

class LinkAdmin(DefaultAdmin):
  list_display = ['get_title', 'url', 'visibility', 'user']

class ListLocationAdmin(DefaultAdmin):
  list_display = ('list', 'location', 'order', 'status')

class ListDistanceAdmin(DefaultAdmin):
  actions = [getData, ]  

class CommentAdmin(DefaultAdmin):
  pass

class DescriptionAdmin(DefaultAdmin):
  pass

admin.site.register(Category, SlugDefaultAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Chain, SlugDefaultAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Geo.Region, SlugDefaultAdmin)
admin.site.register(Tag, SlugDefaultAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(List, SlugDefaultAdmin)
admin.site.register(ListLocation, ListLocationAdmin)
admin.site.register(ListDistance, ListDistanceAdmin)
admin.site.register(Profile)
admin.site.register(VisitedIn, DefaultAdmin)
admin.site.register(Media, DefaultAdmin)
admin.site.register(Description, DescriptionAdmin)
admin.site.register(Size, SlugDefaultAdmin)