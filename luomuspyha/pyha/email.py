#coding=utf-8
from __future__ import unicode_literals
from django.conf import settings
from pyha.models import Collection, Request
from datetime import datetime
import time
from django.core.mail import send_mail
import requests
from requests.auth import HTTPBasicAuth
import json


def send_mail_after_receiving_request(requestId, lang):
	'''
	Sends email after receiving request from Laji.fi to the person who made the request.
	:param requestId: request identifier
	:param lang: language code
	'''	
	req = Request.requests.get(id=requestId)	
	time = req.date.strftime('%d.%m.%Y %H:%I')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		if(req.description != ''):
			subject_content = u"Aineistopyyntö: " + req.description
		else:
			subject_content = u"Aineistopyyntö: " + time
		message = u"Olette tehneet pyynnön salattuun aineistoon Lajitietokeskuksessa "+time+".\nPyyntö tarvitsee teiltä vielä käyttöehtojen hyväksynnän.\n\nOsoite aineistopyyntöön: "+req_link
	elif(lang == 'en'):
		if(req.description != ''):
			subject_content = u"Download request: " + req.description
		else:
			subject_content = u"Download request: " + time
		message = u"You have made a request to download secure FinBIF data on "+time+".\nYou are required to agree to the terms of use.\n\nAddress to your request: "+req_link 
	else:
		if(req.description != ''):
			subject_content = u"På svenska: Aineistopyyntö: " + req.description
		else:
			subject_content = u"På svenska: Aineistopyyntö: " + time
		content = u"På svenska: Olette tehneet pyynnön salattuun aineistoon Lajitietokeskuksessa "+time+".\nPyyntö tarvitsee teiltä vielä käyttöehtojen hyväksynnän.\n\nOsoite aineistopyyntöön: "+req_link
	subject = subject_content	
	from_email = 'helpdesk@laji.fi'	
	to = fetch_email_address(req.user)
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)

def fetch_email_address(personId):
	'''
	fetches email-address for a person registered in Laji.fi
	:param personId: person identifier 
	:returns: person's email-address
	'''
	username = 'pyha'
	password = settings.LAJIPERSONAPI_PW 
	response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ))
	if(response.status_code == 200):
		data = response.json()
		email = data['rdf:RDF']['MA.person']['MA.emailAddress']
		return email
	else:
		print('Sähköpostiosoitteen haku ei onnistunut. HTTP statuskoodi: ' + response.status_code)
		

