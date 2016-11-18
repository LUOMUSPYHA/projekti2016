#coding=utf-8
import requests
from datetime import datetime, date, time
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
import json
import os
from.models import Request
from.models import Collection
from argparse import Namespace
from random import randint

def store(jsond):
		if not checkJson(jsond):
			return
		data = json.loads(jsond, object_hook=lambda d: Namespace(**d))
		if Request.requests.filter(lajiId=os.path.basename(str(data.id))).exists():
			return
		status = getattr(data,'status', 0)
		time = datetime.now()
		
		req = Request()
		req.description=''
		req.lajiId = os.path.basename(str(data.id))
		req.status = status
		req.sensstatus = 0
		req.date = time
		req.source = data.source
		req.user = data.personId
		req.approximateMatches = data.approximateMatches
		req.downloadFormat = getattr(data,'downloadFormat','UNKNOWN')
		req.downloadIncludes = getattr(data,'downloadIncludes','UNKNOWN')
		req.filter_list = makeblob(data.filters)

		req.save()

		if hasattr(data, 'collections'):
                        for i in data.collections:
                        		makeCollection(req, i)
		return req

def makeCollection(req, i):
		co = Collection()
		co.address = os.path.basename(str(i.id))
		co.count = getattr(i, 'count', 0)
		co.status = 0
		co.request = req
		co.downloadRequestHandler = getattr(i, 'downloadRequestHandler', 'none')
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
