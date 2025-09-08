from django import template

register = template.Library()

@register.simple_tag
def mapsmarker(location, visited_locations, loved_locations=None, disliked_locations=None):
  is_activity = location.is_activity

  key = (
    'disliked' if location in disliked_locations else
    'loved' if location in loved_locations else
    'visited' if location.id in visited_locations else
    'default'
  )

  color_map = {
    (True, 'default'):  "rgba(255, 223, 70, 1)",
    (True, 'visited'):  "rgba(255, 236, 140, 0.8)",
    (True, 'loved'):    "rgba(255, 190, 40, 1)",
    (True, 'disliked'): "rgba(180, 160, 30, 0.7)",

    (False, 'default'):  "rgba(0, 102, 255, 1)",
    (False, 'visited'):  "rgba(153, 204, 255, 0.6)",
    (False, 'loved'):    "rgba(0, 70, 180, 1)",
    (False, 'disliked'): "rgba(80, 80, 120, 0.6)",
  }

  return color_map[(is_activity, key)]
