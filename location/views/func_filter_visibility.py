def filter_visibility(user, queryset):
  ''' Add private objects for current user to queryset '''
  if user.is_authenticated:
    ''' Process visibility filters '''
    queryset =  queryset.filter(visibility='p') |\
                queryset.filter(visibility='c') |\
                queryset.filter(visibility='f', user=user) |\
                queryset.filter(visibility='f', user__profile__family=user) |\
                queryset.filter(visibility='q', user=user)
    if hasattr(user, 'profile'):
      ''' Process the dislike filter '''
      if user.profile.hide_least_liked:
        if hasattr(queryset.first(), 'slug'):
          queryset = queryset.exclude(slug__in=user.profile.least_liked.values_list('slug', flat=True))
  else:
    queryset =  queryset.filter(visibility='p')
  return queryset