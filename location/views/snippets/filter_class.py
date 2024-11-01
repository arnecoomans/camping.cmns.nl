# from django.contrib import messages
# from html import escape

class FilterClass:
  def filter_status(self, queryset):
    return queryset.filter(status='p')
  
  def filter_visibility(self, queryset):
    ''' Add private objects for current user to queryset '''
    if self.request.user.is_authenticated:
      ''' Process visibility filters '''
      queryset =  queryset.filter(visibility='p') |\
                  queryset.filter(visibility='c') |\
                  queryset.filter(visibility='f', user=self.request.user) |\
                  queryset.filter(visibility='f', user__profile__family=self.request.user) |\
                  queryset.filter(visibility='q', user=self.request.user)
      if hasattr(self.request.user, 'profile'):
        ''' Process the dislike filter '''
        if self.request.user.profile.hide_least_liked:
          if hasattr(queryset.first(), 'slug'):
            queryset = queryset.exclude(slug__in=self.request.user.profile.least_liked.values_list('slug', flat=True))
          elif 'Comment.Comment' in str(type(queryset.first())):
            queryset = queryset.exclude(location__slug__in=self.request.user.profile.least_liked.values_list('slug', flat=True))
        ''' Process Ignored Tags '''
        if self.request.user.profile.ignored_tags.all().count() > 0:
          if hasattr(queryset.first(), 'tags'):
            queryset = queryset.exclude(tags__in=self.request.user.profile.ignored_tags.all()).exclude(tags__parent__in=self.request.user.profile.ignored_tags.all())
          elif 'Tag.Tag' in str(type(queryset.first())):
            queryset = queryset.exclude(id__in=self.request.user.profile.ignored_tags.values_list('id', flat=True)).exclude(parent__in=self.request.user.profile.ignored_tags.all())
          elif 'Comment.Comment' in str(type(queryset.first())):
            queryset = queryset.exclude(location__tags__in=self.request.user.profile.ignored_tags.all()).exclude(location__tags__parent__in=self.request.user.profile.ignored_tags.all())
    else:
      queryset =  queryset.filter(visibility='p')
    return queryset
  
  def filter(self, queryset):
    queryset = self.filter_status(queryset)
    queryset = self.filter_visibility(queryset)
    return queryset

  def filter_favorites(self, queryset):
    if hasattr(self.request.user, 'profile'):
      return queryset.filter(favorite_of=self.request.user.profile)
    return None
