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
from pyha.models import Collection, Request, RequestLogEntry
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from itertools import chain
from itertools import groupby
from pyha.roles import *
from pyha.email import *

@csrf_exempt
def index(request):
		if check_language(request):
			return HttpResponseRedirect(request.path)
		if not logged_in(request):
			return _process_auth_response(request,'')
		userId = request.session["user_id"]
		lang = request.LANGUAGE_CODE
		hasRole = HANDLER_SENS in request.session.get("user_roles", [None]) or HANDLER_COLL in request.session.get("user_roles", [None])
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			request_list = []
			if HANDLER_SENS in request.session.get("user_roles", [None]):
				request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(taxonSecured__gt = 0).exclude(downloadRequestHandler__contains = str(userId)).values("request")).order_by('-date')
			if HANDLER_COLL in request.session.get("user_roles", [None]):
				request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request")).order_by('-date')
			request_list = list(set(request_list))
			for r in request_list:
				r.email =fetch_email_address(r.user)
			context = {"role": hasRole, "email": request.session["user_email"], "requests": request_list, "static": settings.STA_URL }
			return render(request, 'pyha/handler/index.html', context)
		else:
			request_list = Request.requests.filter(user=userId, status__gte=0).order_by('-date')
			context = {"role": hasRole, "email": request.session["user_email"], "requests": request_list, "static": settings.STA_URL }
			return render(request, 'pyha/index.html', context)

def logout(request):
		if not logged_in(request):
			return _process_auth_response(request, '')
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
		request.session['current_user_role'] = request.POST['role']
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
		if(req):
			send_mail_after_receiving_request(req.id, req.lang)
		return HttpResponse('')


def jsonmock(request):
		return render(request, 'pyha/mockjson.html')
		
def check_language(request):
	if request.GET.get('lang'):
			request.session["_language"] = request.GET.get('lang')
			return True
	return False


def allowed_to_view(request, userRequest, userId, role1, role2):
	if HANDLER_ANY in request.session.get("current_user_role", [None]):
			if not Request.requests.filter(id=userRequest.id, status__gt=0).exists():
				return False
			if role2 and not role1:
				if not Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gt=0).count() > 0:
					return False
	else:
			if not Request.requests.filter(id=userRequest.id, user=userId, status__gte=0).exists() or userRequest.status == -1:
				return False
	if(userRequest.status == -1):
			return False
	return True

@csrf_exempt
def show_request(request):
		if check_language(request):
			return HttpResponseRedirect(request.path)
		#Has Access
		requestId = os.path.basename(os.path.normpath(request.path))
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponseRedirect('/pyha/')
		context = create_request_view_context(request, userRequest, userId, role1, role2)
		#make a log entry
		if userRequest.user != userId:
			make_logEntry_view(request, userRequest, userId, role1, role2)
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			return render(request, 'pyha/handler/requestview.html', context)
		else:
			if(userRequest.status == 0):
				return render(request, 'pyha/requestform.html', context)
			else:
				return render(request, 'pyha/requestview.html', context)

def make_logEntry_view(request, userRequest, userId, role1, role2):
	if not "has_viewed" in request.session:
		request.session["has_viewed"] = []
	if userRequest.id not in request.session.get("has_viewed", [None]):
		logRole = USER
		if role1:
			logRole = HANDLER_SENS
			if role2:
				logRole = HANDLER_BOTH 
		elif role2:
			logRole = HANDLER_COLL
		request.session["has_viewed"].append(userRequest.id)				
		RequestLogEntry.requestLog.create(request=userRequest, user=userId, 
					role=logRole, action=RequestLogEntry.VIEW)

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

def requestLog(request):
		requestId = os.path.basename(os.path.normpath(request.path))
		requestLog_list = list(RequestLogEntry.requestLog.filter(request=requestId))
		email = []
		for l in requestLog_list:
			l.email = fetch_email_address(l.user)
			l.name = fetch_user_name(l.user)
		return requestLog_list

def create_request_view_context(request, userRequest, userId, role1, role2):
		taxonList = []
		customList = []
		collectionList = []
		create_collections_for_lists(request, taxonList, customList, collectionList, userRequest, userId, role1, role2)
		taxon = False
		custom = False
		for collection in collectionList:
			if(collection.taxonSecured > 0):
				taxon = True
			if(collection.customSecured > 0):
				custom = True
		hasRole = role1 or role2
		request_owner = fetch_user_name(userRequest.user)
		request_owners_email = fetch_email_address(userRequest.user)
		context = {"taxonlist": taxonList, "customlist": customList, "taxon": taxon, "custom": custom, "role": hasRole, "role1": role1, "role2": role2, "email": request.session["user_email"], "userRequest": userRequest, "requestLog_list": requestLog(request), "filters": show_filters(request), "collections": collectionList, "static": settings.STA_URL, "request_owner": request_owner, "request_owners_email": request_owners_email}
		return context

def get_values_for_collections(request, List):
	for i, c in enumerate(List):
		c.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(c)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN).json()

def create_collections_for_lists(request, taxonList, customList, collectionList, userRequest, userId, role1, role2):
		hasCollection = False
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			if role1:
				taxonList += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
				hasCollection = True
			customList += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, status__gte=0)
			hasCollection = True
		if not hasCollection:
			taxonList += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
			customList += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, status__gte=0)
			collectionList += Collection.objects.filter(request=userRequest.id, status__gte=0)
		get_values_for_collections(request, collectionList)
		get_values_for_collections(request, customList)
		get_values_for_collections(request, taxonList)

def change_description(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		requestId = request.POST.get('requestid')
		userRequest = Request.requests.get(id = requestId)
		userRequest.description = request.POST.get('description')
		userRequest.save(update_fields=['description'])
		return HttpResponseRedirect(next)

#removes sensitive sightings
def remove_sensitive_data(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0;
		collection.save(update_fields=['taxonSecured'])
		if(collection.customSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(next)

#removes custom sightings
def remove_custom_data(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.customSecured = 0;
		collection.save(update_fields=['customSecured'])
		if(collection.taxonSecured == 0) and (collection.status != -1):
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
		return personId



def removeCollection(request):
	if request.method == 'POST':
		requestId = request.POST.get('requestid')
		collectionId = request.POST.get('collectionid')
		redirect_path = request.POST.get('next')
		collection = Collection.objects.get(address = collectionId, request = requestId)
		#avoid work when submitted multiple times
		if(collection.status != -1):
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
		userRequest = Request.requests.get(id = requestId)
		requestedCollections = request.POST.getlist('checkb');
		if(len(requestedCollections) > 0):
			for rc in requestedCollections:
				if rc not in "sens":
					userCollection = Collection.objects.get(address = rc, request = requestId)
					userCollection.status = 1
					userCollection.save(update_fields=['status'])
				else:
					#userRequest = Request.requests.get(id = requestId)
					userRequest.sensstatus = 1
					userRequest.save(update_fields=['sensstatus'])
			for c in Collection.objects.filter(request = requestId):
				if c.status == 0:
					c.customSecured = 0
					if userRequest.sensstatus == 0:
						c.taxonsecured = 0
					c.save(update_fields=['customSecured'])
					if c.taxonSecured == 0:
						c.status = -1
						c.save(update_fields=['status'])
				#postia vain niille aineistoille, joilla on aineistokohtaisesti salattuja tietoja
				if(c.customSecured > 0):
					send_mail_for_approval(requestId, c, lang)

			userRequest = Request.requests.get(id = requestId)
			userRequest.reason = request.POST.get('reason')
			userRequest.status = 1
			userRequest.save(update_fields=['status','reason'])
			if userRequest.sensstatus == 1:
				send_mail_for_approval_sens(requestId, lang)
			#make a log entry
			RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)

	return HttpResponseRedirect('/pyha/')

def answer(request):
		if request.method == 'POST':
			next = request.POST.get('next', '/')
			collectionId = request.POST.get('collectionid')
			requestId = request.POST.get('requestid')
			if "sens" not in collectionId:
				collection = Collection.objects.get(request=requestId, address=collectionId)
				if request.session["user_id"] in collection.downloadRequestHandler:
					if (int(request.POST.get('answer')) == 1):
						collection.status = 4
						#make a log entry
						RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action =RequestLogEntry.DECISION_POSITIVE)
					else:
						collection.status = 3
						#make a log entry
						RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId),collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action =RequestLogEntry.DECISION_NEGATIVE)
					collection.decisionExplanation = request.POST.get('reason')
					collection.save()
					update(requestId, request.LANGUAGE_CODE)
			elif HANDLER_SENS in request.session["user_roles"]:
				userRequest = Request.requests.get(id = requestId)
				if (int(request.POST.get('answer')) == 1):	
					userRequest.sensstatus = 4
					#make a log entry
					RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_POSITIVE)
				else:
					userRequest.sensstatus = 3
					#make a log entry
					RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_NEGATIVE)
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
		elif (pending == 0 and accepted == 0) and declined > 0:
			wantedRequest.status = 3
		elif accepted > 0 and declined == 0:
			wantedRequest.status = 4
		else:
			wantedRequest.status = 5
		wantedRequest.save()
		
		emailsOnUpdate(requestCollections, wantedRequest, lang, statusBeforeUpdate)
			

"""
	Send "request has been handled" email 
	IF request.sensstatus is 0(no sensitive information) OR 3(declined) OR 4(accepted)  
	AND 
	all it's collections have status != 1(waiting for approval)
"""
def emailsOnUpdate(requestCollections, userRequest, lang, statusBeforeUpdate):
	#count collections that are still waiting for approval
	collectionsNotHandled = len(requestCollections)
	for c in requestCollections:
		if c.status != 1:
			collectionsNotHandled -=1
	#check if request is handled
	if collectionsNotHandled == 0 and (userRequest.sensstatus == 3 or userRequest.sensstatus == 4 or userRequest.sensstatus ==0):
		send_mail_after_request_has_been_handled_to_requester(userRequest.id, lang)
	elif(statusBeforeUpdate!=userRequest.status):
		#Send email if status changed
		send_mail_after_request_status_change_to_requester(userRequest.id, lang)











