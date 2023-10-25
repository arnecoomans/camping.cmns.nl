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

''' Custom Model Admin Classes '''
class LocationAdmin(SlugDefaultAdmin):
  actions = [getAddress, getLatLng, getDistanceFromDepartureCenter, getRegion, clearCachableData]
  list_display = ['name', 'location']
  # def get_readonly_fields(self, request, obj=None):
  #   return [f.name for f in obj._meta.fields if not f.editable]

class ListDistanceAdmin(DefaultAdmin):
  actions = [getData, ]  

class CommentAdmin(DefaultAdmin):
  pass

admin.site.register(Category, SlugDefaultAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Chain, SlugDefaultAdmin)
admin.site.register(Link, DefaultAdmin)
admin.site.register(Geo.Region, SlugDefaultAdmin)
admin.site.register(Tag, SlugDefaultAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(List, SlugDefaultAdmin)
admin.site.register(ListLocation, DefaultAdmin)
admin.site.register(ListDistance, ListDistanceAdmin)
admin.site.register(Profile)
admin.site.register(VisitedIn, DefaultAdmin)