#coding=utf-8
from django.test import TestCase, Client
from django.conf import settings
from pyha.models import Collection, Request
from pyha import warehouse
from django.core import mail
from pyha.test.mocks import *
from pyha.email import send_mail_after_receiving_request
from pyha.email import send_mail_for_approval
import unittest

		
class EmailTesting (TestCase):

	def test_mail_after_receiving_request(self):
		req = warehouse.store(JSON_MOCK4)
		req.description = "Testausta"
		req.save()
		send_mail_after_receiving_request(req.id, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö: Testausta')
		
	def test_mail_send_for_approval(self):
		req = warehouse.store(JSON_MOCK4)
		req.save()
		collections = Collection.objects.filter(request = req.id)
		for c in collections:
			send_mail_for_approval(req.id, c, "fi")
		self.assertEqual(len(mail.outbox), 1)
		msg = mail.outbox[0]
		self.assertEqual(msg.subject, 'Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne')
		self.assertTrue( "testaajapyha@gmail.com" in mail.outbox[0].to )
		self.assertTrue( "pyharengastusdata@gmail.com" in mail.outbox[0].to )			


