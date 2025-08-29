from django import template
''' https://stackoverflow.com/questions/21483003/replacing-a-character-in-django-template '''
register = template.Library()


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
