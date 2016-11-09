#coding=utf-8
import requests
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
from django.core.mail import send_mail
import json
import os
from.models import Request
from.models import Collection
from argparse import Namespace
from random import randint

def store(jsond):
		if not checkJson(jsond):
			return
		x = json.loads(jsond, object_hook=lambda d: Namespace(**d))
		if Request.requests.filter(lajiId=os.path.basename(str(x.id))).exists():
			return
		description = 'kuvaus'
		status = getattr(x,'status', 0)
		time = datetime.now()
		
		req = Request()
		req.lajiId = os.path.basename(str(x.id))
		req.description = description
		req.status = status
		req.sensstatus = 0
		req.date = time
		req.source = x.source
		req.user = x.personId
		req.approximateMatches = x.approximateMatches
		req.downloadFormat = getattr(x,'downloadFormat','UNKNOWN')
		req.downloadIncludes = getattr(x,'downloadIncludes','UNKNOWN')
		req.filter_list = makeblob(x.filters)

		req.save()



		if hasattr(x, 'collections'):
                        for i in x.collections:
                        		makeCollection(req, i)
		make_mail(x, time, req)

def makeCollection(req, i):
		co = Collection()
		co.address = os.path.basename(str(i.id))
		co.description = 'kuvaus'
		co.count = getattr(i, 'count', 0)
		co.status = 0
		co.request = req
		secureReasons = getattr(i, 'mainSecureReasons', 0)
		if(secureReasons != 0):
			taxon = getattr(secureReasons, 'DEFAULT_TAXON_CONSERVATION', 0)
			custom = getattr(secureReasons, 'CUSTOM', 0)
			if(taxon != 0):
				co.taxonSecured = getattr(taxon, 'count', 0)
			if(custom != 0):
				co.customSecured = getattr(custom, 'count', 0)
		if hasattr(i, 'mainSecureReasons'):
			co.secureReasons = getattr(i, 'mainSecureReasons').__dict__
			for key in co.secureReasons:
				co.secureReasons[key]=0
		else:
			co.secureReasons = "{'none': 1}"
		co.save()

def make_mail(x, time, req):
		subject = getattr(x, 'description', time.strftime('%d.%m.%Y %H:%I'))
		req_link = settings.REQ_URL+str(req.id)
		message_content = u"Olette tehneet pyynnön salattuun aineistoon Lajitietokeskuksessa "+time.strftime('%d.%m.%Y %H:%I')+u".\nPyyntö tarvitsee teiltä vielä ehtojen hyväksynnän.\nOsoite aineistopyyntöön "+subject+": "+req_link+ "\n\nYou have made a request to download secure FinBIF data on "+time.strftime('%d.%m.%Y %H:%I')+".\nYou are required to agree to the terms of use.\nAddress to your request "+subject+": "+req_link 
		message = message_content
		from_email = 'helpdesk@laji.fi'
		recipients = [x.email]
		mail = send_mail(subject, message, from_email, recipients, fail_silently=False)
		return mail

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"personId":','"approximateMatches":','"filters":'] 
		if all(x in jsond for x in wantedFields):
			return True
		return False
		
def makeblob(x):
		blob = "{"
		for i, text in enumerate(x):
			if not(i == 0):
					blob += ","
			blob += '"' + list(vars(x[i]).keys())[0] + '":['
			if isinstance(getattr(x[i], list(vars(x[i]).keys())[0]), (list)):
				for l,text in enumerate(getattr(x[i], list(vars(x[i]).keys())[0])):
					if not(l == 0):
						blob += ","
					blob += '"'+text+'"'
			else:
				blob += '"'+getattr(x[i], list(vars(x[i]).keys())[0])+'"'
			blob += "]"
		blob += "}"
		return blob
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
