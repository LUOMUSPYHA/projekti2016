#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
import unittest

class RequestTesting(TestCase):
	def setUp(self):
		self.client = Client() 
		session = self.client.session
		session['user_name'] = 'paisti'
		session['user_id'] = 'MA.309'
		session['user_email'] = 'ex.apmle@example.com'
		session['token'] = 'asd213'
		session.save()
		warehouse.store(JSON_MOCK)
		
	def test_requests_collections_secure_reason_amounts_are_saved(self):
		warehouse.store(JSON_MOCK6)
		col1 = Collection.objects.get(address="colcustomsec1")
		col2 = Collection.objects.get(address="colsecured")
		self.assertEqual(col1.customSecured, 1)
		self.assertEqual(col2.customSecured, 2)
		self.assertEqual(col2.taxonSecured, 3)
		

	def test_request_has_its_own_page(self):
		response = self.client.get('/pyha/request/1')
		self.assertEqual(len(Request.requests.all()), 1)
		self.assertEqual(response.status_code, 200)

	def test_user_can_only_see_their_own_requests(self):
		warehouse.store(JSON_MOCK2)
		response = self.client.get('/pyha/')
		self.assertEqual(len(Request.requests.all()), 2)
		self.assertContains(response, "1 742")

	def test_request_with_missing_attributes_is_not_saved(self):
		warehouse.store(JSON_MOCK3)
		response = self.client.get('/pyha/')
		self.assertEqual(len(Request.requests.all()), 1)
		self.assertNotContains(response, "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555")

	def test_requests_collections_are_shown_in_its_page(self):
		response = self.client.get('/pyha/request/1')
		self.assertContains(response, "Pyyntöön sisältyvät aineistot:")
		self.assertContains(response, "Talvilintulaskenta")
		self.assertContains(response, "Hatikka.fi")
		self.assertContains(response, "Lintujen ja nisäkkäiden ruokintapaikkaseuranta")
		