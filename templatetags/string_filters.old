from django import template
register = template.Library()

@register.filter
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)

@register.simple_tag
def objreplace(value, what, to):
  """
  Replace substring in value.
  Usage in template:
    {% objreplace app.url_format "{address}" location.address %}
  """
  return str(value).replace(str(what), str(to))