from django.utils.translation import gettext_lazy as _

''' Translation Cheat Class
    This class holds translations for often used terms from database content.
    By storing these terms in this class, it will appear via django-admin makemessages -a
    and retain the translations when translating.
'''

class Translations:
  translations = [
    # Countries
    _('Netherlands'),
    _('Belgium'),
    _('Germany'),
    _('France'),
    _('Spain'),
    _('Italy'),
    _('United Kingdom'),
    _('United States'),
    _('Canada'),
    _('Australia'),
    _('Indonesia'),

    # Regions
    _('Vosges'),

    # Locations
    _('Bed & Breakfast'),
    _('Camping'),
    _('Hotel'),
    _('Chalet'),
    _('Gite'),
    _('Glamping (Safaritent)'),
    _('Mobile Home'),
    _('Resort'),
    _('Villa'),

    # Activities
    _('Sight-to-seen'),
    _('Transit (one nighter)'),
    _('Beach'),
    _('City'),
    _('Museum'),
    _('Park'),
    _('Rest-stop'),
    _('Restaurant'),
    _('Sauna'),
    _('Shop'),
    _('Swimmingpool'),
    _('Theatre'),
    _('Theme-park'),
    _('Village'),
    _('Winery'),
    _('Zoo'),
  ]