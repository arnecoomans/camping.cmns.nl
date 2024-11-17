from django.views.generic import View
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
from openai import OpenAI

from ..snippets.filter_class import FilterClass
from location.models.Location import Location, Category, Chain
# from location.models.Tag import Tag
# from location.models.Comment import Comment
from .jsonhelper import JSONHelper

''' JSONGetLocationDescription
    This view is used to fetch a location description from an exernal source.
'''

class JSONGetLocationDescription(JSONHelper, View):

  def __get_promt(self, location):
    prompt = f"Schrijf een korte, aantrekkelijke beschrijving van "
    if not location.category.name.lower() in location.name.lower():
      prompt += f"{ location.category } "
    prompt += f"{ location.name }, een { location.category.name.lower() } in { location.department() }."
    prompt += "Benadruk de sfeer, gezinsvriendelijke voorzieningen, belangrijke faciliteiten, "
    prompt += "en nabijgelegen bezienswaardigheden. Houd de toon uitnodigend en informatief."
    return prompt

  def __get_chatgpt_response(self, prompt):
    # client = OpenAI(
    #   api_key=settings.CHATGPT_API_KEY
    # )
    # try:
    #   # Call the ChatGPT API
    #   response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #       {"role": "system", "content": "Je bent een behulpzame AI-assistent."},
    #       {"role": "user", "content": prompt}
    #     ],
    #     max_tokens=150,
    #     temperature=0.7,
    #     )
    #   # Extract and return the description
    #   return response
    #   return response['choices'][0]['message']['content'].strip()
    # except Exception as e:
    #  self.messages.append(('danger', 'ChatGPT error: ' + str(e)))
    #  self.return_response()
    #  return str(e)
    return 'chat gpt completion not yet supported'
  
  def get(self, request, *args, **kwargs):
    response = {
      '__meta': {
        'location': str(self.get_object()),
        'prompt': self.__get_promt(self.get_object())
      },
      'gpt': self.__get_chatgpt_response(self.__get_promt(self.get_object()))
    }
    return JsonResponse(response)