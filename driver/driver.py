import platform
import os
import urllib.request
from urllib.parse import urlparse
import requests
import posixpath
from zipfile import ZipFile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils.log import Log as log

available_drivers = {"firefox", "chrome"}


class WebDriverConfig:

	def __init__(self, config):
		self.driver = config['internal']['driver']
		self.source = None
		self.selenium_instance = None

	def check_driver_availability(self):
		return True

	def attach_selenium(self):
		if self.driver == "firefox":
			desired = DesiredCapabilities.FIREFOX
			desired["loggingPrefs"] = {"browser": "ALL"}
			options = FirefoxOptions()
			options.headless = True
			options.add_argument("--start-maximized")
			options.add_argument("--disable-infobars")
			logs_dir = "logs"
			if not os.path.exists(logs_dir):
				os.mkdir(logs_dir)
			log.info("Attaching selenium to driver")
			self.selenium_instance = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options, log_path=logs_dir)
		if self.driver == "chrome":
			options = ChromeOptions()
			options.add_argument("--headless")
			options.add_argument("--log-level=3")
			options.add_experimental_option("excludeSwitches", ["enable-logging"])
			logs_dir = "logs"
			if not os.path.exists(logs_dir):
				os.mkdir(logs_dir)
			log.info("Attaching selenium to driver")
			self.selenium_instance = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=options)

	def dispose(self):
		if self.selenium_instance:
			log.info("Shutting down selenium")
			self.selenium_instance.quit()
