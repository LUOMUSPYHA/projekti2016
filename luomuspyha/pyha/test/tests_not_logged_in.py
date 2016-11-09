#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
import unittest

class NotLoggedInTests(TestCase):
	def setUp(self):
		self.client = Client() 

	def test_not_logged_in_gets_redirected(self):
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next=')
