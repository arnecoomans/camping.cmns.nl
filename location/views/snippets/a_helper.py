from django.contrib import messages
from html import escape
from django.http import JsonResponse

from location.models.Location import Location

class aHelper:
  def getDefaultData(self, status=1):
    data = {
      'request': {
        'request': self.request.resolver_match.view_name,
        'location': self.kwargs['location'] if 'location' in self.kwargs else None,
        'params': self.request.GET,
      },
      'status': {
        'code': status, # 1 = success, 0 = error
        'name': 'success' if status == 1 else 'error',
        'message': 'Request handled successfully' if status == 1 else 'Request failed',
      },
      'data': {},
    }
    return data

  def verifyUserAuthenticated(self):
    if not self.request.user.is_authenticated:
      response = self.getDefaultData(0)
      response['status']['message'] = 'User not logged in'
      return JsonResponse(response)
    return True

  def getLocation(self):
    try:
      location = Location.objects.get(slug=self.kwargs['location'] if 'location' in self.kwargs else self.request.GET.get('location', None))
    except Location.DoesNotExist:
      return False
    return location
  
  def getLocationError(self):
    response = self.getDefaultData(0)
    response['status']['message'] = 'Location not found'
    return JsonResponse(response)

  def getInputError(self, field, message=None):
    response = self.getDefaultData(0)
    response['status']['message'] = f'No {field} provided or supplied input is invalid'
    if message:
      response['status']['message'] = f"{ response['status']['message'] }: { message }"
    return JsonResponse(response)