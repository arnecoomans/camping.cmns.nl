def order_media(queryset):
  order = ['q', 'f', 'c', 'p']
  result_list = []
  for visibility in order:
    for item in queryset.filter(visibility=visibility):
      result_list.append(item)
  return result_list
