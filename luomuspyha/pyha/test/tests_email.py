#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
from pyha.email import send_mail_after_receiving_request
import unittest

		
class EmailTesting (TestCase):

	def test_mail_(self):
		req = warehouse.store(JSON_MOCK4)
		
		send_mail_after_receiving_request(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö: Testausta')
		


