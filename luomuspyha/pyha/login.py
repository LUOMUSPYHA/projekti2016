import requests
from django.shortcuts import redirect
from django.conf import settings
import json

def _get_authentication_info(request, token):
   url = settings.LAJIAUTH_URL + "token/" + token

   response = requests.get(url)

   if response.status_code != 200:
       return None
   else:
       content = json.loads(response.content.decode('utf-8'))
       return content
		
def log_in(request, content):
   if not "user_id" in request.session:
       request.session["user_id"] = content["user"]["qname"]
       request.session["user_name"] = content["user"]["name"]
       request.session["user_email"] = content["user"]["email"]
       request.session["user_roles"] = content["user"]["roles"]
       if not request.session["user_roles"]:
          request.session["user_roles"] = ['user']
          request.session["user_role"] = 'user'
       else:
          request.session["user_role"] = content["user"]["roles"][0]
          request.session["user_roles"].append('user')
       request.session.set_expiry(3600)
       return True
   return False

def log_out(request):
   '''
   Clear session for the request.
   :param request:
   :return: true if user was succesfully logged out
   '''
   if "user_id" in request.session:     
       del request.session["user_id"]      
       del request.session["user_name"]
       del request.session["user_email"]
       return True
   return False

def authenticate(request, token):
   '''
   Logs user in if the token is valid.
   :param request: A HttpRequest to create session for
   :param token: The token returned by LajiAuth.
   :return: true if user is authenticated succesfully
   '''
   result = _get_authentication_info(request, token)
   if result is None:
       return False
   else:
       log_in(request, result)
       return True

def authenticated(request):
   '''
   Checks if user is authenticated if MOCK_AUTHENTICATION is set to 'Skip', always returns true,
   :param request:
   :return:
   '''
   if settings.MOCK_AUTHENTICATION == "Skip": return True
   else :return "user_id" in request.session

def get_user_name(request):
   if "user_name" in request.session:
       return request.session["user_name"]

