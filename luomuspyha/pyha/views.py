from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pyha.login import authenticate
from pyha.login import log_out


@require_http_methods(["GET"])
def index(request):
	context = {"title": "Tervetuloa " + request.session["user_name"] , "message": "pyhaton salaista tekstia juuri sinulle", "target_header":"Valitsemasi target: ", "targets": ['linnut','nisakkaat'], "collection_header":"Valitsemasi aineisto: ", "collections": ['ain1', 'ain2', 'ain3']}
	if not "user_id" in request.session:
                return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next&allowUnapproved=true')
	return render(request, 'pyha/index.html', context)

def login(request):      
	return _process_auth_response(request)

def logout(request):
        context = {"title": "Kirjaudu ulos", "message": "Kirjauduit ulos onnistuneesti"}
        log_out(request)
        return render(request, 'pyha/index.html', context)


def _process_auth_response(request):
    if not "token" in request.POST:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next&allowUnapproved=true')
    if authenticate(request, request.POST["token"]):
        return HttpResponseRedirect('pyha/index')
    else:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next')

def receiver(request):

        print(request)
        #data = json.loads(request.body)
        #filters = data['filters']
        #collections = data ['collections']
        return HttpResponse('')
	
