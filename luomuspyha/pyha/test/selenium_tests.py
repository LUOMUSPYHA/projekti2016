# coding=utf-8
import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import WebDriverException
from datetime import datetime
import time


class Requestlist_TestCase(unittest.TestCase):
	
	def setUp(self):	
		# vaihda oma chromedriverin osoite ennen ajamista		
		chromedriver = "/home/ad/fshome5/u5/r/rivorivo/Linux/Python/envi3/lib/python3.4/site-packages/chromedriver/bin/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		self.driver = webdriver.Chrome(chromedriver)
		driver = self.driver
		driver.get("http://127.0.0.1:8000/mock/jsonmock")
		driver.find_element_by_xpath("/html/body/form[1]").submit()
		driver.get("http://127.0.0.1:8000/pyha/")
		driver.find_element_by_id("local-login").click()
		elem = driver.find_element_by_id("login-form")
		email = driver.find_element_by_name("email")
		password = driver.find_element_by_name("password")
		email.send_keys("pyhatestaaja@gmail.com")
		password.send_keys("L4ausesuomeksi")
		elem.submit()

	def test_request_link_visible(self):	
		driver = self.driver
		teksti = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[1]')
		self.assertEqual('kuvaus',teksti.text)
	
	def test_status(self):
		driver = self.driver
		teksti = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[4]')
		self.assertEqual("You haven't accepted the conditions",teksti.text)
	
	def test_paivaus_fiksusti(self):
		driver = self.driver
		teksti = driver.find_element_by_xpath('//table[1]/tbody[1]/tr[1]/td[2]')
		datetime.strptime(teksti.text, "%d.%m.%Y %H:%M")
		
	def tearDown(self):
		self.driver.close()

class Requestpage_TestCase(unittest.TestCase):
	
	def setUp(self):			
		chromedriver = "/home/ad/fshome5/u5/r/rivorivo/Linux/Python/envi3/lib/python3.4/site-packages/chromedriver/bin/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		self.driver = webdriver.Chrome(chromedriver)
		driver = self.driver
		driver.get("http://127.0.0.1:8000/mock/jsonmock")
		driver.find_element_by_xpath("/html/body/form[1]").submit()
		driver.get("http://127.0.0.1:8000/pyha/")
		driver.find_element_by_id("local-login").click()
		elem = driver.find_element_by_id("login-form")
		email = driver.find_element_by_name("email")
		password = driver.find_element_by_name("password")
		email.send_keys("pyhatestaaja@gmail.com")
		password.send_keys("L4ausesuomeksi")
		elem.submit()
		driver.get("http://127.0.0.1:8000/pyha/request/1")

	def test_rajauksetNapista(self):
		driver = self.driver
		nappi = driver.find_element_by_xpath('/html/body/div[1]/div[1]/button[1]')
		nappi.click()
		kohde = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/table[1]')	
		self.assertIn('Filter Values',kohde.text)

	def test_ehtojenHyvaksynta(self):
		driver= self.driver
		nappi = driver.find_element_by_xpath("//form[@id='requestform']/div[1]/table[1]/tbody/tr[2]/td[5]/button[1]")	
		nappi.click()	
		time.sleep(3)	
		checkbox = driver.find_element_by_id("checkb0")
		checkbox.click()
		tila = driver.find_element_by_id("statustext0")
		self.assertEqual(tila.text, "You accepted the terms of use")

	def test_perustelutPakko(self):
		driver= self.driver
		driver.get("http://127.0.0.1:8000/pyha/request/1")	
		nappi = driver.find_element_by_xpath("//form[@id='requestform']/div[1]/table[1]/tbody/tr[2]/td[5]/button[1]")	
		nappi.click()	
		time.sleep(2)	
		checkbox = driver.find_element_by_id("checkb0")
		checkbox.click()
		time.sleep(2)
		try:
			driver.find_element_by_id("submit").click()
			message = "ok"
		except 	WebDriverException:
			message = "error"
		self.assertNotEqual(message,"ok")
		self.assertEqual(message,"error")

	def tearDown(self):
		self.driver.close()

class Languages_TestCase(unittest.TestCase):

	def setUp(self):			
		chromedriver = "/home/ad/fshome5/u5/r/rivorivo/Linux/Python/envi3/lib/python3.4/site-packages/chromedriver/bin/chromedriver"
		os.environ["webdriver.chrome.driver"] = chromedriver
		self.driver = webdriver.Chrome(chromedriver)
		driver = self.driver
		driver.get("http://127.0.0.1:8000/mock/jsonmock")
		driver.find_element_by_xpath("/html/body/form[1]").submit()
		driver.get("http://127.0.0.1:8000/pyha/")
		driver.find_element_by_id("local-login").click()
		elem = driver.find_element_by_id("login-form")
		email = driver.find_element_by_name("email")
		password = driver.find_element_by_name("password")
		email.send_keys("pyhatestaaja@gmail.com")
		password.send_keys("L4ausesuomeksi")
		elem.submit()

	def test_kielenNimiVaihtuu(self):
		driver=self.driver
		kieli = driver.find_element_by_xpath('//*[@id="language_form"]/button[1]')
		self.assertEqual(kieli.text,"en")
		kielinappi = driver.find_element_by_xpath('//*[@id="navbar"]/ul[2]/div[1]')
		kielinappi.click()
		suomi = driver.find_element_by_xpath('//*[@id="myDropdown"]/a[1]')
		suomi.click()
		kieli = driver.find_element_by_xpath('//*[@id="language_form"]/button[1]')
		self.assertEqual(kieli.text,"fi")
		kielinappi = driver.find_element_by_xpath('//*[@id="navbar"]/ul[2]/div[1]')
		kielinappi.click()
		ruotsi = driver.find_element_by_xpath('//*[@id="myDropdown"]/a[3]')
		ruotsi.click()
		kieli = driver.find_element_by_xpath('//*[@id="language_form"]/button[1]')
		self.assertEqual(kieli.text,"sw")

	def test_sivunKieliVaihtuu(self):
		driver=self.driver
		osumia = driver.find_element_by_xpath('//*[@id="requests-table"]/thead[1]/tr[1]/th[3]')
		kuvaus = driver.find_element_by_xpath('//*[@id="requests-table"]/thead[1]/tr[1]/th[1]')
		self.assertEqual(osumia.text,"Matches")
		self.assertEqual(kuvaus.text,"Description")
		kielinappi = driver.find_element_by_xpath('//*[@id="navbar"]/ul[2]/div[1]')
		kielinappi.click()
		suomi = driver.find_element_by_xpath('//*[@id="myDropdown"]/a[1]')
		suomi.click()
		osumia = driver.find_element_by_xpath('//*[@id="requests-table"]/thead[1]/tr[1]/th[3]')
		kuvaus = driver.find_element_by_xpath('//*[@id="requests-table"]/thead[1]/tr[1]/th[1]')
		self.assertEqual(osumia.text,"Osumia")
		self.assertEqual(kuvaus.text,"Kuvaus")

	def tearDown(self):
		self.driver.close()

if __name__ == "__main__":
    unittest.main()