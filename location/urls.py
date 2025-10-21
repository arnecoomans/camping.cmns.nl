from django.urls import path

from . import views

app_name = 'location'

urlpatterns = [
  path('', views.LocationListView.as_view(), name='home'),
  path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

  path('locations/', views.LocationListView.as_view(), name='locations'),
  path('locations/<country>/', views.LocationListView.as_view(), name='ListLocationsByCountry'),
  path('locations/<country>/<region>/', views.LocationListView.as_view(), name='ListLocationsByRegion'),
  path('locations/<country>/<region>/<department>/', views.LocationListView.as_view(), name='ListLocationsByDepartment'),
  # path('locations/a/suggest', views.aSuggestLocations.as_view(), name='aListLocationSuggestions'),

  path('map/', views.LocationMapView.as_view(), name='locationsMap'),
  path('map/<country>/', views.LocationMapView.as_view(), name='ListLocationsByCountryMap'),
  path('map/<country>/<region>/', views.LocationMapView.as_view(), name='ListLocationsByRegionMap'),
  path('map/<country>/<region>/<department>/', views.LocationMapView.as_view(), name='ListLocationsByDepartmentMap'),

  path('location/add/', views.AddLocation.as_view(), name='AddLocation'),
  
  path('location/<str:slug>/', views.LocationView.as_view(), name='location'),
  path('location/<str:slug>/edit/', views.EditLocation.as_view(), name='EditLocation'),
  path('location/<str:slug>/list/', views.AddLocationToList.as_view(), name='LocationAddList'),

  path('location/<str:slug>/reset/', views.ResetLocationData.as_view(), name='ResetLocation'),
  path('location/<str:slug>/distance_to_home/', views.GetDistanceToHome.as_view(), name='DistanceToHome'),
  path('location/<str:slug>/description/add/', views.AddDescriptionToLocation.as_view(), name='AddDescriptionToLocation'),
  path('location/description/add:<int:pk>/', views.AddLocationToDescription.as_view(), name='AddLocationToDescription'),
  path('location/description/edit:<int:pk>/', views.editDescription.as_view(), name='EditDescription'),
  # path('location/<str:slug>/description/toggle:<int:descriptionid>/', views.deleteDescriptionFromLocation.as_view(), name='deleteDescriptionFromLocation'),
  path('location/<str:slug>/links/add/', views.addLinkToLocation.as_view(), name='AddLinkToLocation'),
  path('location/<str:slug>/links/delete:<linkid>/', views.deleteLinkFromLocation.as_view(), name='DeleteLinkFromLocation'),
  path('location/<location_slug>/links/edit:<pk>/', views.editLinkAtLocation.as_view(), name='EditLinkAtLocation'),

  path('activities/', views.ActivityListView.as_view(), name='activities'),
  path('activities/<country>/', views.ActivityListView.as_view(), name='ListActivitiesByCountry'),
  path('activities/<country>/<region>/', views.ActivityListView.as_view(), name='ListActivitiesByRegion'),
  path('activities/<country>/<region>/<department>/', views.ActivityListView.as_view(), name='ListLActivitiesByDepartment'),

  path('activity/add/', views.AddLocation.as_view(), name='AddActivity'),
  path('activity/<str:slug>/', views.LocationView.as_view(), name='activity'),
  path('activity/<str:slug>/edit/', views.EditActivity.as_view(), name='EditActivity'),

  path('search/', views.AllSearchView.as_view(), name='search'),
  path('search/<country>/', views.AllSearchView.as_view(), name='SearchByCountry'),
  path('search/<country>/<region>/', views.AllSearchView.as_view(), name='SearchByRegion'),
  path('search/<country>/<region>/<department>/', views.AllSearchView.as_view(), name='SearchByDepartment'),

  path('comment/add/', views.AddComment.as_view(), name='AddComment'),
  path('comment/<pk>/edit/', views.EditComment.as_view(), name='EditComment'),
  path('comments/', views.CommentListView.as_view(), name='comments'),
  path('comments/by:<username>/', views.CommentByUserListView.as_view(), name='CommentsByUser'),
  
  path('tags/', views.TagListView.as_view(), name='tags'),
  path('tags/add/to:<str:slug>/', views.AddTagToLocation.as_view(), name='AddTagToLocation'),
  path('tag/add/', views.AddTag.as_view(), name='AddTag'),
  path('tag/add/to:<str:slug>/', views.AddTag.as_view(), name='AddTagTo'),
  path('tag/<str:slug>/', views.TagView.as_view(), name='tag'),
  path('tag/<str:slug>/edit/', views.EditTag.as_view(), name='EditTag'),
  # path('tag/<str:slug>/delete/', views.ToggleDeleteTag.as_view(), name='ToggleDeleteTag'),
  # path('a/tags/suggest/', views.aSuggestTags.as_view(), name='aListTagSuggestions'),
  # path('a/<location>/tag/suggest/', views.aSuggestTags.as_view(), name='aListTagSuggestionsFor'),
  # path('a/<location>/tag/list/', views.aListTags.as_view(), name='aListTagsFor'),
  # path('a/<location>/tag/', views.aAddTag.as_view(), name='aAddTag'),
  

  path('lists/', views.ListListView.as_view(), name='lists'),
  path('list/favorites/', views.AutomatedFavoriteList.as_view(), name="ListFavorites"),
  path('list/add/', views.AddList.as_view(), name='AddList'),
  path('list/add/<location>', views.AddList.as_view(), name='AddListWithLocation'),
  path('list/<str:slug>/', views.ListDetailView.as_view(), name='list'),
  path('list/<str:slug>/edit/', views.EditList.as_view(), name='EditList'),
  path('list/<str:slug>/start-from-home/', views.StartListFromHome.as_view(), name='StartListFromHome'),
  path('list/<str:slug>/end-at-home/', views.EndListAtHome.as_view(), name='EndListAtHome'),
  path('list/<str:slug>/delete/', views.DeleteList.as_view(), name='DeleteList'),
  path('list/<str:slug>/undelete/', views.UndeleteList.as_view(), name='UndeleteList'),
  path('list/<str:slug>/add/', views.AddLocationToList.as_view(), name='GetAddLocationToList'),
  path('list/<str:slug>/add/<location>/', views.AddLocationToList.as_view(), name='AddLocationToList'),
  path('list/<str:slug>/<pk>:<location>/edit/', views.EditListLocation.as_view(), name="EditListLocation"),
  path('list/<str:slug>/<pk>:<location>/delete/', views.DeleteLocationFromList.as_view(), name='DeleteLocationFromList'),
  path('list/<str:slug>/<id>:<location>/up/', views.ListLocationUp.as_view(), name="ListLocationUp"),
  path('list/<str:slug>/<id>:<location>/down/', views.ListLocationDown.as_view(), name="ListLocationDown"),

  path('profile/', views.ProfileView.as_view(), name='profile'),
  # path('profile/family/<id>/', views.ToggleFamilyMember.as_view(), name='ToggleFamily'),
  # path('profile/favorite/<str:slug>/', views.ToggleFavorite.as_view(), name='ToggleFavorite'),
  # path('profile/least-like/<str:slug>/', views.ToggleLeastLiked.as_view(), name='ToggleLeastLiked'),
  path('profile/visit/add/', views.AddVisit.as_view(), name='AddVisit'),
  path('profile/visit/edit:<pk>/', views.EditVisit.as_view(), name='EditVisit'),

  # path('profile/visit/delete:<pk>/', views.ToggleDeletedVisit.as_view(), name='DeleteVisit'),
  path('session/allow_google_maps/', views.ToggleGoogleMapsSession.as_view(), name='MapsPermissionSession'), #Profile
  path('profile/allow_google_maps//', views.ToggleGoogleMapsProfile.as_view(), name='MapsPermissionProfile'), #Profile
  # path('a/profile/favorite/<location>/', views.aToggleFavorite.as_view(), name='aToggleFavorite'),

  path('chain/add/', views.AddChain.as_view(), name='AddChainTo'),
  path('chain/add/<str:slug>/', views.AddChain.as_view(), name='AddChainTo'),
  
  path('stack/add/<str:slug>/', views.AddMediaToLocation.as_view(), name='AddMediaToLocation'),
  path('stack/list/<str:slug>/', views.StackView.as_view(), name='MediaStack'),
  path('stack/refresh/<str:slug>:<pk>/', views.MediaRefreshView.as_view(), name='MediaRefresh'),
  # path('media/delete/<object_slug>:<pk>', views.ToggleMediaDeleted.as_view(), name='MediaDelete'),
  path('image/<str:filename>', views.MediaStreamView.as_view(), name='MediaStream'),
  path('register/', views.SignUpView.as_view(), name='register'),

  # Toggle Views 
  # Toggle Deleted
  # path('json/toggle/<str:model>/<int:pk>/delete/', views.ToggleDeleted.as_view(), name='ToggleDeleted'),
  # path('json/toggle/<str:model>/<str:slug>/delete/', views.ToggleDeleted.as_view(), name='ToggleDeletedBySlug'),
  # # Toggle field of model, optionally with slug and value
  # path('json/toggle/<str:model>:<str:slug>/<str:field>/', views.ToggleAttribute.as_view(), name='ToggleAttributeWithSlug'),
  # path('json/toggle/<str:model>:<str:slug>/<str:field>/<value>/', views.ToggleAttribute.as_view(), name='ToggleAttributeWithSlugWithValue'),
  # path('json/toggle/<str:model>/<str:field>/', views.ToggleAttribute.as_view(), name='ToggleAttribute'),
  # path('json/toggle/<str:model>/<str:field>/<value>/', views.ToggleAttribute.as_view(), name='ToggleAttributeWithValue'),
  


  # Async Views
  ## JSONGetLocationAttributes Functions: fetch a list of attibutes for a location
  ## Triggered in the getLocationAttributes.js script
  ## Handled by the JSONGetLocationAttributes view in location/views/json/getlocationattributes.py
  # path('json/attributes/<str:location>/<str:attribute>/', views.JSONGetLocationAttributes.as_view(), name='getAttributesFor'),
  # path('json/suggestions/<str:model>/for:<str:location>/', views.JSONGetLocationAttributeSuggestions.as_view(), name='getSuggestionsFor'),
  # path('json/suggestions/', views.JSONGetLocationSuggestions.as_view(), name='getLocationSuggestions'),
  # path('json/options/<str:model>/for:<str:location>/', views.JSONGetAttributeOptions.as_view(), name='getOptionsFor'),
  # path('json/options/<str:model>/', views.JSONGetAttributeOptions.as_view(), name='getOptions'),
  # path('json/get/<str:model>:<str:slug>/description/', views.JSONGetLocationDescription.as_view(), name='getLocationDescription'),
  ## Comments
  # path('a/comments/', views.aListComments.as_view(), name='aListComments'),
  # path('json/<location>/comments/', views.aListComments.as_view(), name='aListCommentsFor'),
  # path('json/<location>/comment/', views.aAddComment.as_view(), name='aAddComment'),

  ## Action List
  # path('a/<str:location>/actionlist/', views.JsonActionList.as_view(), name='getActionlist'),
]