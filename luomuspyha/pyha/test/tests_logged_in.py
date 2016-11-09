#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
import unittest


class LoggedInTests(TestCase):
	def setUp(self):
		self.client = Client() 
		session = self.client.session
		session['user_name'] = 'paisti'
		session['user_id'] = 10
		session['user_email'] = 'ex.apmle@example.com'
		session['token'] = 'asd213'
		session.save()

	def test_user_sees_the_index_page(self):
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 200)

	def test_user_correct_message_when_theres_no_request(self):
		response = self.client.get('/index/')
		self.assertContains(response, "ei ole pyyntöjä")


	def test_logging_out_clears_session_information(self):
		self.client.post('/logout/')
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next=')
		