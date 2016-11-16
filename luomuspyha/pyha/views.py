import json
import os
import requests
import ast
import time
from luomuspyha import secrets
from argparse import Namespace
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pyha.login import authenticate
from pyha.login import log_out
from requests.auth import HTTPBasicAuth
from pyha.email import fetch_email_address
from pyha.warehouse import store
from pyha.models import Collection, Request
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from itertools import chain
from itertools import groupby

from pyha.email import *

@csrf_exempt
def index(request):
		if not logged_in(request):
			return _process_auth_response(request,'')
		userId = request.session["user_id"]
		lang = request.LANGUAGE_CODE
		if request.GET.get('lang'):
			request.session["_language"] = request.GET.get('lang')		
			return HttpResponseRedirect(request.path)
		hasRole = secrets.ROLE_1 in request.session.get("user_roles", [None]) or secrets.ROLE_2 in request.session.get("user_roles", [None])
		if 'handler' in request.session.get("user_role", [None]):
			request_list = []
			if secrets.ROLE_1 in request.session.get("user_roles", [None]):
				request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(taxonSecured__gt = 0).exclude(downloadRequestHandler__contains = str(userId)).values("request")).order_by('-date')
			if secrets.ROLE_2 in request.session.get("user_roles", [None]):
				request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request")).order_by('-date')
			context = {"role": hasRole, "email": request.session["user_email"], "requests": request_list, "static": settings.STA_URL }
			return render(request, 'pyha/role1/index.html', context)
		else:
			request_list = Request.requests.filter(user=userId, status__gte=0).order_by('-date')
			context = {"role": hasRole, "email": request.session["user_email"], "requests": request_list, "static": settings.STA_URL }
			return render(request, 'pyha/index.html', context)

def login(request):
		return _process_auth_response(request, '')

def logout(request):
		if not logged_in(request):
			return _process_auth_response(request, '')
		context = {"title": "Kirjaudu ulos", "message": "Kirjauduit ulos onnistuneesti", "static": settings.STA_URL}
		log_out(request)
		return HttpResponseRedirect("https://beta.laji.fi/")

def logged_in(request):
		if "user_id" in request.session:
			return True
		return False

def change_role(request):
		if not logged_in(request) and not 'role' in request.POST:
			return HttpResponse('/')
		next = request.POST.get('next', '/pyha/')
		request.session['user_role'] = request.POST['role']
		return HttpResponseRedirect(next)


def _process_auth_response(request, indexpath):
		if not "token" in request.POST:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
		if authenticate(request, request.POST["token"]):
			return HttpResponseRedirect('/pyha/'+indexpath)
		else:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
@csrf_exempt
def receiver(request):
		if 'JSON' in request.POST:
			text = request.POST['JSON']
			jsond = text
			req = store(jsond)
		else:
			jsond = request.body.decode("utf-8")
			req = store(jsond)
		data = json.loads(jsond, object_hook=lambda d: Namespace(**d)) #kielen takia
		if 'locale' in data:
			lang = data.locale	
		else:
			lang = 'fi'
		send_mail_after_receiving_request(req.id, lang)	
		return HttpResponse('')


def jsonmock(request):
		return render(request, 'pyha/mockjson.html')
@csrf_exempt
def show_request(request):
		requestId = os.path.basename(os.path.normpath(request.path))
		userRequest = Request.requests.get(id=requestId)
		#Has Access
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		if request.GET.get('lang'):
			request.session["_language"] = request.GET.get('lang')		
			return HttpResponseRedirect(request.path)
		userId = request.session["user_id"]
		if 'handler' in request.session.get("user_role", [None]):
			if not Request.requests.filter(id=userRequest.id, status__gte=0).exists():
				return HttpResponseRedirect('/pyha/')
			if secrets.ROLE_2 in request.session.get("user_roles", [None]) and not secrets.ROLE_1 in request.session.get("user_roles", [None]):
				if not Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gt=0).count() > 0:
					return HttpResponseRedirect('/pyha/')
		else:
			if not Request.requests.filter(id=userRequest.id, user=userId, status__gte=0).exists():
				return HttpResponseRedirect('/pyha/')
		if(userRequest.status == -1):
			return HttpResponseRedirect('/pyha/')
		#Create list
		hasCollection = False
		collectioncount = 0
		if 'handler' in request.session.get("user_role", [None]):
			if secrets.ROLE_1 in request.session.get("user_roles", [None]):
				collectionList = Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
				collectioncount += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gt=0).count()
				hasCollection = True
			if secrets.ROLE_2 in request.session.get("user_roles", [None]):
				collectionList = Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gte=0)
				collectioncount += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gt=0).count()
				hasCollection = True
		if not hasCollection:
			collectionList = Collection.objects.filter(request=userRequest.id, status__gte=0)
			collectioncount = Collection.objects.filter(request=userRequest.id, status__gt=0).count()
		for i, c in enumerate(collectionList):
			c.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(c)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN).json()			
		taxon = False
		for collection in collectionList:
			if(collection.taxonSecured > 0):
				taxon = True
		hasRole = secrets.ROLE_1 in request.session.get("user_roles", [None]) or secrets.ROLE_2 in request.session.get("user_roles", [None])
		request_owner = fetch_user_name(userRequest.user)
		request_owners_email = fetch_email_address(userRequest.user)
		context = {"collectioncount": collectioncount, "taxon": taxon, "role": hasRole, "role2": secrets.ROLE_2 in request.session.get("user_roles", [None]), "email": request.session["user_email"], "userRequest": userRequest, "filters": show_filters(request), "collections": collectionList, "static": settings.STA_URL, "request_owner": request_owner, "request_owners_email": request_owners_email}
                    
		if 'handler' in request.session.get("user_role", [None]):
                    return render(request, 'pyha/role1/requestview.html', context)
		else:
                    if(userRequest.status == 0):
                        return render(request, 'pyha/requestform.html', context)
                    else:
                        return render(request, 'pyha/requestview.html', context)
                        
def show_filters(request):
		requestId = os.path.basename(os.path.normpath(request.path))
		userRequest = Request.requests.get(id=requestId)
		filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		filters = requests.get(settings.LAJIFILTERS_URL)
		filterResultList = list(range(len(vars(filterList).keys())))
		lang = request.LANGUAGE_CODE
		filtersobject = json.loads(filters.text, object_hook=lambda d: Namespace(**d))
		for i, b in enumerate(vars(filterList).keys()):
			languagelabel = b
			filternamelist = getattr(filterList, b)
			if b in filters.json():
				filterfield = getattr(filtersobject, b)
				label = getattr(filterfield, "label")
				if(lang == 'sw'):
					languagelabel = getattr(label, "sv")
				else:
					languagelabel = getattr(label, request.LANGUAGE_CODE)
				if "RESOURCE" in getattr(filterfield, "type"):
					resource = getattr(filterfield, "resource")
					for k, a in enumerate(getattr(filterList, b)):
						if resource.startswith("metadata"):
							filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN)
							kaannoslista = []
							filtername = str(a)
							for ii in filterfield2.json():
								if (str(a) == ii['id']):
									filtername = ii['value']
									break
						else:
							if(lang == 'sw'):
								filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=sv&access_token="+secrets.TOKEN)
							else:
								filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN)
							filternameobject = json.loads(filterfield2.text, object_hook=lambda d: Namespace(**d))
							filtername = getattr(filternameobject, "name", str(a))
						filternamelist[k]= filtername
			tup = (b, filternamelist, languagelabel)
			filterResultList[i] = tup
		return filterResultList

def change_description(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		requestId = request.POST.get('requestid')
		userRequest = Request.requests.get(id = requestId)
		userRequest.description = request.POST.get('description')
		userRequest.save(update_fields=['description'])
		return HttpResponseRedirect(next)

def remove_sensitive_data(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0;
		collection.save(update_fields=['taxonSecured'])
		if(collection.customSecured == 0):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(next)

def remove_custom_data(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.customSecured = 0;
		collection.save(update_fields=['customSecured'])
		if(collection.taxonSecured == 0):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(next)


def fetch_user_name(personId):
	'''
	fetches user name for a person registered in Laji.fi
	:param personId: person identifier 
	:returns: person's full name
	'''
	username = 'pyha'
	password = settings.LAJIPERSONAPI_PW 
	response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ))
	if(response.status_code == 200):
		data = response.json()
		name = data['rdf:RDF']['MA.person']['MA.fullName']
		return name
	else:
		print('Nimen haku ei onnistunut. HTTP statuskoodi: ' + response.status_code)



def removeCollection(request):
	if request.method == 'POST':
		requestId = request.POST.get('requestid')
		collectionId = request.POST.get('collectionid')
		redirect_path = request.POST.get('next')
		print("Deleting collection:")
		print("request_id: " + requestId)
		print("address: " + collectionId)
		collection = Collection.objects.get(address = collectionId, request = requestId)
		collection.status = -1
		collection.save(update_fields=['status'])
		check_all_collections_removed(requestId)
		return HttpResponseRedirect(redirect_path)



#check if all collections have status -1. If so set status of request to -1.
def check_all_collections_removed(requestId):
		userRequest = Request.requests.get(id = requestId)
		collectionList = userRequest.collection_set.filter(status__gte=0 )
		if not collectionList:
			userRequest.status = -1
			userRequest.save(update_fields=['status'])

def approve(request):
	if request.method == 'POST':
		lang = 'fi' #ainakin toistaiseksi
		requestId = request.POST.get('requestid')
		requestedCollections = request.POST.getlist('checkb');
		if(len(requestedCollections) > 0):
			for i in requestedCollections:
				send_mail_for_approval(requestId, i, lang)
				if i not in "sens":
					userCollection = Collection.objects.get(address = i, request = requestId)
					userCollection.status = 1
					userCollection.save(update_fields=['status'])
				else:
					userRequest = Request.requests.get(id = requestId)
					userRequest.sensstatus = 1
					userRequest.save(update_fields=['sensstatus'])
			for i in Collection.objects.filter(request = requestId):
				if i.status == 0:
					i.customSecured = 0
					i.save(update_fields=['customSecured'])
					if i.taxonSecured == 0:
						i.status = -1
						i.save(update_fields=['status'])
				userRequest = Request.requests.get(id = requestId)
				userRequest.reason = request.POST.get('reason')
				userRequest.status = 1
				userRequest.save(update_fields=['status','reason'])
			if userRequest.sensstatus == 1:
				send_mail_for_approval_sens(requestId, lang)
	return HttpResponseRedirect('/pyha/')

def answer(request):
		if request.method == 'POST':
			next = request.POST.get('next', '/')
			collectionId = request.POST.get('collectionid')
			requestId = request.POST.get('requestid')
			if "sens" not in collectionId:
				collection = Collection.objects.get(request=requestId, address=collectionId)
				if (int(request.POST.get('answer')) == 1):
					collection.status = 4
				else:
					collection.status = 3
				collection.decisionExplanation = request.POST.get('reason')
				collection.save()
				update(requestId, request.LANGUAGE_CODE)
			else:
				userRequest = Request.requests.get(id = requestId)
				if (int(request.POST.get('answer')) == 1):	
					userRequest.sensstatus = 4
				else:
					userRequest.sensstatus = 3
				userRequest.sensDecisionExplanation = request.POST.get('reason')
				userRequest.save()
				update(requestId, request.LANGUAGE_CODE)
		return HttpResponseRedirect(next)

def update(requestId, lang):
		#for both sensstatus and collection status
		#status 0: Ei sensitiivistä tietoa
		#status 1: Odottaa aineiston toimittajan käsittelyä
		#status 2: Osittain hyväksytty
		#status 3: Hylätty
		#status 4: Hyväksytty
		
		wantedRequest = Request.requests.get(id=requestId)
		#tmp variable for checking if status changed
		statusBeforeUpdate = wantedRequest.status
		requestCollections = Collection.objects.filter(request=requestId)
		accepted = 0
		declined = 0
		pending = 0
		if wantedRequest.sensstatus == 1:
			pending += 1
		elif wantedRequest.sensstatus == 2:
			accepted += 1
			declined += 1
		elif wantedRequest.sensstatus == 3:
			declined += 1
		elif wantedRequest.sensstatus == 4:
			accepted += 1
		for c in requestCollections:
			if c.status == 1:
				pending += 1
			elif c.status == 2:
				accepted += 1
				declined += 1
			elif c.status == 3:
				declined += 1
			elif c.status == 4:
				accepted += 1

		if accepted == 0 and declined == 0:
			wantedRequest.status = 1
		elif accepted > 0 and (declined > 0 or pending > 0):
			wantedRequest.status = 2
		elif accepted == 0 and declined > 0:
			wantedRequest.status = 3
		elif accepted > 0 and declined == 0:
			wantedRequest.status = 4
		else:
			wantedRequest.status = 5
		wantedRequest.save()
		
		#Send email if status changed
		if(statusBeforeUpdate!=wantedRequest.status):
			send_mail_after_request_status_change_to_requester(wantedRequest.id, lang)
			













