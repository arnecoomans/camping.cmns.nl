from django import template

register = template.Library()

@register.filter
def find_distance(location, user):
  """
  Finds the distance object where the user's home matches the destination or origin.
  """
  try:
    if not user.is_authenticated:
      return None
    if not hasattr(user, 'profile'):
      return None
    for distance in location.dest_origin.all():
      if distance.destination == user.profile.home:
        return (distance.getDistance(), distance.getTime())
    for distance in location.dest_destination.all():
      if distance.origin == user.profile.home:
        return (distance.distance, distance.time, distance)
  except AttributeError:
    return None
