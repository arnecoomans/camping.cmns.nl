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
    else:
      queryset =  queryset.filter(visibility='p')
    return queryset
