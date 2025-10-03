from django import template

register = template.Library()

''' Update Query Params 
    Allows to add and remove qyery parameters from the current URL
    keeping the other parameters intact.
'''

@register.simple_tag
def update_query_params(request, add=None, remove=None, to=None, replace=None, active_filters=[]):
    query_params = request.GET.copy()
    
    # Add url based filters to the query parameters
    augment_url = []
    if len(active_filters) > 0:
      if 'country' in active_filters:
        augment_url.append(active_filters['country'])
        if 'region' in active_filters:
          augment_url.append(active_filters['region'])
          if 'department' in active_filters:
            augment_url.append(active_filters['department'])
    if len(augment_url) > 0:
      augment_url.append('')

    # If no parameters are provided, return the current URL parameters
    if not add and not remove and not replace:
      return len(query_params) > 0 and f"{ '/'.join(augment_url) }?{ query_params.urlencode() }" or ''
    
    # Ensure the 'to' argument is provided (the parameter to modify)
    if not to:
      raise ValueError("You must provide a 'to' argument specifying which query parameter to modify.")

    # Handle adding a value to the specified parameter (e.g., 'tags' or 'category')
    if add:
      existing_values = query_params.get(to, '').split(',')
      if add not in existing_values:
        if existing_values == ['']:  # Handle the case where the list is empty
          existing_values = [add]
        else:
          existing_values.append(add)
        query_params[to] = ','.join(existing_values)
    
    # Handle removing a value from the specified parameter
    if remove:
      existing_values = query_params.get(to, '').split(',')
      if remove in existing_values:
        existing_values.remove(remove)
        if existing_values:
          query_params[to] = ','.join(existing_values)
        else:
          query_params.pop(to)
    
    # Handle replacing the value of the specified parameter
    if replace:
      query_params[to] = replace
      
    return len(query_params) > 0 and f"{ '/'.join(augment_url) }?{ query_params.urlencode() }" or f"{ '/'.join(augment_url) }"
    