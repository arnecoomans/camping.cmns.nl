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

  path('location/add/', views.AddLocation.as_view(), name='AddLocation'),
  path('location/<slug>/', views.LocationView.as_view(), name='location'),
  path('location/<slug>/edit/', views.EditLocation.as_view(), name='EditLocation'),
  path('location/<slug>/list/', views.AddLocationToList.as_view(), name='LocationAddList'),

  path('location/<slug>/toggle/category/', views.ToggleCategory.as_view(), name='ToggleCategoryForm'),
  path('location/<slug>/toggle/category/<object_slug>/', views.ToggleCategory.as_view(), name='ToggleCategory'),
  path('location/<slug>/toggle/chain/', views.ToggleChain.as_view(), name='ToggleChainForm'),
  path('location/<slug>/toggle/chain/<object_slug>/', views.ToggleChain.as_view(), name='ToggleChain'),
  path('location/<slug>/toggle/tag/', views.ToggleTag.as_view(), name='ToggleTagForm'),
  path('location/<slug>/toggle/tag/<object_slug>/', views.ToggleTag.as_view(), name='ToggleTag'),
  path('location/<slug>/reset/', views.ResetLocationData.as_view(), name='ResetLocation'),
  

  path('activities/', views.ActivityListView.as_view(), name='activities'),
  path('activities/<country>/', views.ActivityListView.as_view(), name='ListActivitiesByCountry'),
  path('activities/<country>/<region>/', views.ActivityListView.as_view(), name='ListActivitiesByRegion'),
  path('activities/<country>/<region>/<department>/', views.ActivityListView.as_view(), name='ListLActivitiesByDepartment'),

  path('activity/add/', views.AddLocation.as_view(), name='AddActivity'),
  path('activity/<slug>/', views.LocationView.as_view(), name='activity'),
  path('activity/<slug>/edit/', views.EditActivity.as_view(), name='EditActivity'),

  path('search/', views.LocationSearchView.as_view(), name='search'),
  path('search/<country>/', views.LocationSearchView.as_view(), name='SearchByCountry'),
  path('search/<country>/<region>/', views.LocationSearchView.as_view(), name='SearchByRegion'),
  path('search/<country>/<region>/<department>/', views.LocationSearchView.as_view(), name='SearchByDepartment'),

  path('comment/add/', views.AddComment.as_view(), name='AddComment'),
  path('comment/<pk>/delete/', views.DeleteComment.as_view(), name='DeleteComment'),
  path('comment/<pk>/undelete/', views.UndeleteComment.as_view(), name='UndeleteComment'),
  path('comment/<pk>/edit/', views.EditComment.as_view(), name='EditComment'),
  path('comments/', views.CommentListView.as_view(), name='comments'),
  path('comments/by:<username>/', views.CommentByUserListView.as_view(), name='CommentsByUser'),

  path('tags/', views.TagListView.as_view(), name='tags'),
  path('tag/add/', views.AddTag.as_view(), name='AddTag'),
  path('tag/add/<slug>/', views.AddTag.as_view(), name='AddTagTo'),
  path('tag/<slug>/', views.TagView.as_view(), name='tag'),
  path('tag/<slug>/edit/', views.EditTag.as_view(), name='EditTag'),
  path('tag/<slug>/delete/', views.ToggleDeleteTag.as_view(), name='ToggleDeleteTag'),


  path('lists/', views.ListListView.as_view(), name='lists'),
  path('list/add/', views.AddList.as_view(), name='AddList'),
  path('list/add/<location>', views.AddList.as_view(), name='AddListWithLocation'),
  path('list/<slug>/', views.ListDetailView.as_view(), name='list'),
  path('list/<slug>/edit/', views.EditList.as_view(), name='EditList'),
  path('list/<slug>/start-from-home/', views.StartListFromHome.as_view(), name='StartListFromHome'),
  path('list/<slug>/end-at-home/', views.EndListAtHome.as_view(), name='EndListAtHome'),
  path('list/<slug>/delete/', views.DeleteList.as_view(), name='DeleteList'),
  path('list/<slug>/undelete/', views.UndeleteList.as_view(), name='UndeleteList'),
  path('list/<slug>/add/', views.AddLocationToList.as_view(), name='GetAddLocationToList'),
  path('list/<slug>/add/<location>/', views.AddLocationToList.as_view(), name='AddLocationToList'),
  path('list/<slug>/<pk>:<location>/delete/', views.DeleteLocationFromList.as_view(), name='DeleteLocationFromList'),
  path('list/<slug>/<id>:<location>/up/', views.ListLocationUp.as_view(), name="ListLocationUp"),
  path('list/<slug>/<id>:<location>/down/', views.ListLocationDown.as_view(), name="ListLocationDown"),

  path('profile/', views.ProfileView.as_view(), name='profile'),
  path('profile/family/<id>/', views.ToggleFamilyMember.as_view(), name='ToggleFamily'),
  path('profile/favorite/<slug>/', views.ToggleFavorite.as_view(), name='ToggleFavorite'),
  path('profile/least-like/<slug>/', views.ToggleLeastLiked.as_view(), name='ToggleLeastLiked'),
  path('profile/visit/add/', views.AddVisit.as_view(), name='AddVisit'),
  path('profile/visit/edit:<pk>/', views.EditVisit.as_view(), name='EditVisit'),
  path('profile/visit/delete:<pk>/', views.ToggleDeletedVisit.as_view(), name='DeleteVisit'),

  path('chain/add/', views.AddChain.as_view(), name='AddChainTo'),
  path('chain/add/<slug>/', views.AddChain.as_view(), name='AddChainTo'),

  path('register/', views.SignUpView.as_view(), name='register'),
]