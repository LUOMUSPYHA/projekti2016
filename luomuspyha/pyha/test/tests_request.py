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
		self.assertContains(response, "Pyyntöösi sisältyvät havainnot:")
		self.assertContains(response, "Talvilintulaskenta")
		self.assertContains(response, "Hatikka.fi")
		self.assertContains(response, "Lintujen ja nisäkkäiden ruokintapaikkaseuranta")
		
	def test_collection_has_correct_secure_reason_amounts(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colcustomsec1")
		self.assertEqual(col.customSecured, 1)
		self.assertEqual(col.taxonSecured, 0)
		
	def test_collection_has_correct_secure_reason_amounts2(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colsecured")
		self.assertEqual(col.customSecured, 2)
		self.assertEqual(col.taxonSecured, 3)
		
	def test_collections_sensitive_secure_reasons_can_be_deleted(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colsecured")
		self.assertEqual(col.customSecured, 2)

		response = self.client.post('/pyha/removeCustom', {'collectionId': col.id})
		col = Collection.objects.all().get(address="colsecured")

		self.assertEqual(col.customSecured, 0)
		

	def test_collections_sensitive_secure_reasons_can_be_deleted(self):
		warehouse.store(JSON_MOCK6)
		col = Collection.objects.all().get(address="colsecured")
		self.assertEqual(col.taxonSecured, 3)

		response = self.client.post('/pyha/removeSens', {'collectionId': col.id})
		col = Collection.objects.all().get(address="colsecured")

		self.assertEqual(col.taxonSecured, 0)

	def test_requests_filters_labels_and_values_comes_from_apitest(self):
		warehouse.store(JSON_MOCK7)
		response = self.client.get('/pyha/request/2')
		print(response)
		self.assertContains(response, "Pyyntösi rajaukset:")
		self.assertContains(response, "Vain salatut")
		self.assertContains(response, "true")
		self.assertContains(response, "Lajin hallinnollinen rajaus")
		self.assertContains(response, "Uhanalainen laji (LSA Liite 4)")
		self.assertContains(response, "Lajiryhmä")
		self.assertContains(response, "Käet")
		self.assertContains(response, "Jyrsijät")
		self.assertContains(response, "Aika")
		self.assertContains(response, "2000/")

