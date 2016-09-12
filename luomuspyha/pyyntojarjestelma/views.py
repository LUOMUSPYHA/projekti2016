from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def index(request):
    #render(request, 'pyyntojarjestelma/index.html',
	#{}, RequestContext(request))
	context = {}
	return render(request, 'pyyntojarjestelma/index.html', context)
