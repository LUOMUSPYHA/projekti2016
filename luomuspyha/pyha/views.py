from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings


@require_http_methods(["GET"])
def index(request):
	#render(request, 'pyha/index.html',
	#{}, RequestContext(request))
	context = {}
	return render(request, 'pyha/index.html', context)
def login(request):
    
	if request.method == 'POST':
		return _process_auth_response(request)


	else:
		return redirect(login)

	#render(request, 'pyha/index.html',
	#{}, RequestContext(request))
	'''context = {}
	return render(request, 'pyha/index.html', context)'''



def _process_auth_response(request):
    if not "token" in request.POST:
        return redirect(settings.LAJIAUTH_URL+'login?target='+TARGET+'&next')
    if authenticate(request, request.POST["token"]):
        return redirect(index)
    else:
        return redirect(settings.LAJIAUTH_URL+'login?target='+TARGET+'&next')
