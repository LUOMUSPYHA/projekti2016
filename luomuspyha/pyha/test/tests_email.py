#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
import unittest

		
class EmailTesting (TestCase):
	def setUp(self):
		warehouse.store(JSON_MOCK4)

	def test_mail_(self):
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Testausta')
		#self.assertItemsEqual(msg.recipients, ['te.staaja@example.com'])
