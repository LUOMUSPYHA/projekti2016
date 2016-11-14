#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
from pyha.email import send_mail_after_receiving_request
from pyha.email import fetch_email_address
import unittest
import mock

#mock method
def fake_fetch_email_address(personId):
	return 'test123@321.asdfgh'

def get()

class EmailTesting (TestCase):

	def setUp(self):
		self.client = Client() 
		session = self.client.session
		session['user_name'] = 'paisti'
		session['user_id'] = 'MA.309'
		session['user_email'] = 'te.staaja@example.com'
		session['token'] = 'asd213'
		session.save()
	
	def test_send_mail_after_receiving_request(self):
		req = warehouse.store(JSON_MOCK4)
		req.description = "Testausta"
		req.save()
		send_mail_after_receiving_request(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö: Testausta')
		
	
	#does not test fetch_email_address
	@mock.patch("pyha.email.fetch_email_address", fake_fetch_email_address)
	def test_mail_is_actually_sent_when_request_is_recieved(self):
		json_str= JSON_MOCK4
		self.client.post('/api/request/', data= json_str, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.to, ['test123@321.asdfgh'])
	
	
