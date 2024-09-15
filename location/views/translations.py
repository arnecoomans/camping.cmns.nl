from django.utils.translation import gettext_lazy as _

''' Cheat Class
    This class holds translations for often used terms from database content.
    By storing these terms in this class, it will appear via django-admin makemessages -a
    and retain the translations when translating.
'''

class Translations:
  translations = [
    _('Netherlands'),
    _('Belgium'),
    _('Germany'),
    _('France'),
    _('Spain'),
    _('Italy'),

    _('Vosges'),
  ]