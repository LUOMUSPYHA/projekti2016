#coding=utf-8
from __future__ import unicode_literals
from django.conf import settings
from luomuspyha import secrets
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
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		if(req.description != ''):
			subject_content = u"Aineistopyyntö: " + req.description
		else:
			subject_content = "uAineistopyyntö: " + time
		message = u"Olette tehneet pyynnön salattuun aineistoon Lajitietokeskuksessa "+time+".\nPyyntö tarvitsee teiltä vielä käyttöehtojen hyväksynnän.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		if(req.description != ''):
			subject_content = u"Download request: " + req.description
		else:
			subject_content = u"Download request: " + time
		message = u"You have made a request to download secure FinBIF data on "+time+".\nYou are required to agree to the terms of use.\n\nAddress to your request: "+req_link+"?lang=en" 
	else:
		if(req.description != ''):
			subject_content = u"På svenska: Aineistopyyntö: " + req.description
		else:
			subject_content = u"På svenska: Aineistopyyntö: " + time
		content = u"På svenska: Olette tehneet pyynnön salattuun aineistoon Lajitietokeskuksessa "+time+".\nPyyntö tarvitsee teiltä vielä käyttöehtojen hyväksynnän.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"
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
		
def send_mail_for_approval(requestId, collection, lang):
	'''
	Sends mail to collection owner(s) for request approval
	:param requestId: request identifier 
	:param collection: collection address
	:param lang: language code
	'''	
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)	
	if(lang == 'fi'):
		subject = "Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = "Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Download request from FinBIF waits for approval decision"
		message = u"Download request sent from Finnish Biodiversity Info Faculty at "+time+" waits for your approval decision.\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"På svenska: Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = u"På svenska: Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
	recipients = []
	response = requests.get(settings.LAJIAPI_URL+"collections/"+str(collection)+"?access_token="+secrets.TOKEN)
	if(response.status_code == 200):
		data = response.json()
		if 'downloadRequestHandler' in data:
			handlers = data['downloadRequestHandler']
			for personId in handlers:
				email = fetch_email_address(personId)
				recipients.append(email)
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)

	
def send_mail_for_approval_sens(requestId, lang):
	'''
	Sends mail to sensitive information approval request handler(s) for request approval
	:param requestId: request identifier 
	:param lang: language code
	'''	
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)	
	if(lang == 'fi'):
		subject = "Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = "Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö koskien sensitiivistä aineistoa odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Download request from FinBIF waits for approval decision"
		message = u"Download request sent from Finnish Biodiversity Info Faculty at "+time+" concerning sensitive data waits for your approval decision.\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"På svenska: Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = u"På svenska: Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö koskien sensitiivistä aineistoa odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
	to = fetch_email_address('MA.319')  #odottaa parannuksia
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)	
	

def send_mail_after_request_status_change_to_requester(requestId, lang):
	'''
	Sends mail to person who made the request when request status changes
	:param requestId: request identifier 
	:param collections: list of collection addresses
	:param lang: language code
	'''	
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		subject = u"Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut"
		message = u"Lajitietokeskukseen "+time+" tekemäsi aineistopyynnön tila on muuttunut.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Status change in download request from FinBIF"
		message = u"Status change in request sent from Finnish Biodiversity Info Faculty at "+time+".\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"På svenska: Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut"
		message = u"På svenska: Lajitietokeskukseen "+time+" tekemäsi aineistopyynnön tila on muuttunut.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
	to = fetch_email_address(req.user)
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)






















