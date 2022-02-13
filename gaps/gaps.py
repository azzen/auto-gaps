import os
import zlib
import json
from collections import Counter

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from hooks import hook as hk
from bs4 import BeautifulSoup as bs
from utils.log import Log as log


def crc32(filename, chunk_size=65536):
	if os.path.exists(filename):
		with open(filename, 'rb') as f:
			checksum = 0
			while chunk := f.read(chunk_size):
				checksum = zlib.crc32(chunk, checksum)
			return checksum
	return 0


class Gaps:
	sleep_time = 5

	def __init__(self, selenium_instance, user_config):
		self.config = user_config
		self.instance = selenium_instance
		self.connected = False

	def connect(self):
		self.instance.get(self.config['internal']['gaps_url'])
		start_idp = self.instance.find_element(By.XPATH, '//input[@name="Login"]')
		select = Select(self.instance.find_element(By.XPATH, '//select[@name="user_idp"]'))
		select.select_by_value(self.config['internal']['gaps_provider_url'])
		start_idp.click()
		try:
			WebDriverWait(self.instance, 10).until(
				ec.presence_of_element_located((By.ID, "login-button")))
		except TimeoutException:
			log.err("Couldn't load gaps provider, aborting.")
			return
		email_input = self.instance.find_element(By.XPATH, '//input[@name="j_username"]')
		password_input = self.instance.find_element(By.XPATH, '//input[@name="j_password"]')
		login_button = self.instance.find_element(By.XPATH, '//button[@name="_eventId_proceed"]')
		email_input.send_keys(self.config['user']['email'])
		password_input.send_keys(self.config['user']['password'])
		login_button.click()
		try:
			WebDriverWait(self.instance, 10).until(
				ec.presence_of_element_located((By.CLASS_NAME, "titreBox")))
		except TimeoutException:
			log.err("Couldn't load GAPS, aborting.")
			return
		log.success("Successfully logged to GAPS")
		self.connected = True

	def get_grades(self):
		if not self.connected:
			raise "Not connected to GAPS."
		self.instance.get(self.config['internal']['gaps_grades_url'])
		try:
			WebDriverWait(self.instance, 30).until(
				ec.presence_of_element_located((By.CLASS_NAME, "displayArray")))
		except TimeoutException:
			log.err("Couldn't load grades.")
			return dict()
		soup = bs(self.instance.page_source, "html.parser")
		table = soup.find("table", {"class": "displayArray"})
		grades = dict()
		last_category = ""
		last_key = ""

		for tr in table.find_all("tr"):
			first = tr.find_all('td')[0]
			last = tr.find_all('td')[-1] if len(tr.find_all('td')) > 1 else first
			if first.get('class')[0] == "bigheader":
				last_key = first.decode_contents().split()[0]
				grades[last_key] = {'course': [], 'lab': []}
			if 'Cours' in first.decode_contents().split()[0]:
				last_category = 'course'
			elif 'Laboratoire' in first.decode_contents().split()[0]:
				last_category = 'lab'
			if last.get('class')[0] == 'bodyCC' and ((grade := last.decode_contents().split()[0]) != "-"):
				grades[last_key][last_category].append(grade)
		return grades

	def save(self, grades):
		log.info('Saving new grades')
		data = json.dumps(grades)
		save_path = self.config['internal']['data_file']
		save_dir = os.path.dirname(save_path)
		if not os.path.exists(save_dir):
			os.makedirs(save_dir)
		with open(save_path, 'w') as f:
			f.write(data)
			f.close()
			log.success('Successfully saved new grades')

	def compare_grades(self, new):
		file_csm = crc32(self.config['internal']['data_file'])
		if file_csm == 0:  # no file to compare with
			return -1, {}

		new_grades_csm = zlib.crc32(bytearray(json.dumps(new).encode()))
		if file_csm == new_grades_csm:
			return 0, {}

		old = json.load(open(self.config['internal']['data_file'], 'r'))

		def ldiff(l1, l2, k, d, cat):
			if k not in d:
				d[k] = dict()
			c1 = Counter(l1)
			c2 = Counter(l2)
			difference = c2 - c1
			d[k][cat] = list(difference.elements())

		def diff(g1, g2):
			delta = {}
			for k, v in g1.items():
				if k not in g1:
					delta[k] = v.copy()
				if k in g1 and len(g2[k]['course']) > len(v['course']):
					ldiff(g1[k]['course'], g2[k]['course'], k, delta, 'course')
				if k in g1 and len(g2[k]['lab']) > len(v['lab']):
					ldiff(g1[k]['lab'], g2[k]['lab'], k, delta, 'lab')
			return delta

		new_grades_to_notify = diff(old, new)
		if len(new_grades_to_notify) > 0:
			return 1, new_grades_to_notify
		else:  # a grade might have been modified
			return -1, {}  # force save new grades

	def notify(self, new_grades):
		for service in self.config['hooks'].keys():
			h = hk.Hook(service, self.config, new_grades)
			h.notify(h.format())
