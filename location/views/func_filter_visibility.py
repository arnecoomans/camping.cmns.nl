def filter_visibility(user, queryset):
    ''' Add private objects for current user to queryset '''
    if user.is_authenticated:
      ''' Process visibility filters '''
      queryset =  queryset.filter(visibility='p') |\
                  queryset.filter(visibility='c') |\
                  queryset.filter(visibility='f', user=user) |\
                  queryset.filter(visibility='f', user__profile__family=user) |\
                  queryset.filter(visibility='q', user=user)
    else:
      queryset =  queryset.filter(visibility='p')
    return queryset