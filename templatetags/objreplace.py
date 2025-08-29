# templatetags/objreplace.py
from django import template

register = template.Library()

@register.simple_tag
def objreplace(value, what, to):
  """
  Replace substring in value.
  Usage in template:
    {% objreplace app.url_format "{address}" location.address %}
  """
  return str(value).replace(str(what), str(to))
