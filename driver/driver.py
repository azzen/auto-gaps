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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils.log import Log as log

available_drivers = {"firefox", "chrome"}
sources_list = {
	"webdriver/geckodriver_linux32/geckodriver": "https://api.github.com/repos/mozilla/geckodriver/releases/latest",
	"webdriver/geckodriver_linux64/geckodriver": "https://api.github.com/repos/mozilla/geckodriver/releases/latest",
	"webdriver/geckodriver_win32/geckodriver.exe": "https://api.github.com/repos/mozilla/geckodriver/releases/latest",
	"webdriver/geckodriver_win64/geckodriver.exe": "https://api.github.com/repos/mozilla/geckodriver/releases/latest",
	"webdriver/chromedriver_linux64/chromedriver": "https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
	"webdriver/chromedriver_win/chromedriver.exe": "https://chromedriver.storage.googleapis.com/LATEST_RELEASE",
}


class WebDriverConfig:

	def __init__(self, config):
		self.driver = config['internal']['driver']
		self.source = None
		self.selenium_instance = None

	def check_driver_availability(self):
		system = platform.system()
		arch = platform.architecture()[0]
		if self.driver == "firefox":
			if system == "Windows" and arch == "32bit":
				self.source = "webdriver/geckodriver_win32/geckodriver.exe"
			elif system == "Windows" and arch == "64bit":
				self.source = "webdriver/geckodriver_win64/geckodriver.exe"
			else:
				raise Exception(f"Failed to find your OS [{system} {arch}]")
		if self.driver == "chrome":
			if system == "Windows":
				self.source = "webdriver/chromedriver_win/chromedriver.exe"
			elif system == "Linux" and arch == "64bits":
				self.source = "webdriver/chromedriver_linux64/chromedriver"
			else:
				raise Exception("Failed to find an appropriate driver for your OS")
		if not os.path.exists(self.source):
			log.warn(f"Web driver '{self.source}' not found.")
			log.info(f"Getting package from: {sources_list[self.source]}")
			download_url = None
			if "googleapis.com" in sources_list[self.source]:
				response = requests.get(sources_list[self.source])
				if response.status_code != 200:
					raise Exception("Could not fetch googleapis.com...")
				version = response.text
				filename = "chromedriver_linux64.zip" if system == "Linux" else "chromedriver_win32.zip"
				download_url = urllib.parse.urljoin("https://chromedriver.storage.googleapis.com/",
													posixpath.join(version, filename))
				log.info(f"Downloading latest release from googleapis.com: {download_url}")
			if "api.github.com" in sources_list[self.source]:
				response = requests.get(sources_list[self.source]).json()
				if len(response) == 0:
					raise Exception("Could not fetch api.github.com...")
				log.info("Getting latest release from api.github.com.")
				for v in response["assets"]:
					if system in v["name"] or (system[0:2]).lower() in v["name"] and arch[0:1] in v["name"]:
						download_url = v["browser_download_url"]
				if download_url:
					log.info(f"Downloading latest release from api.github.com: {download_url}")
				else:
					log.err("Download has failed aborting...")
					return False
			driver_dir = os.path.dirname(self.source)
			if not os.path.exists(driver_dir):
				os.makedirs(driver_dir)
			filename = os.path.basename(urlparse(download_url).path)
			download_path = os.path.join(driver_dir, filename)
			urllib.request.urlretrieve(download_url, download_path)
			if os.path.splitext(download_path)[1] == ".zip":
				log.info("Extracting zip file.")
				with ZipFile(download_path, 'r') as ar:
					ar.extractall(driver_dir)
					log.success("Extracted zip file.")
				log.info("Cleaning up directory.")
				os.remove(download_path)
				log.success("Successfully downloaded the driver.")
			else:
				log.success("Successfully downloaded the driver.")
			return True
		else:
			log.info("Driver found: ", self.source)
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
			self.selenium_instance = webdriver.Firefox(executable_path=self.source,
													   service_log_path=os.path.join(logs_dir, "geckodriver.log"),
													   options=options)
		if self.driver == "chrome":
			options = ChromeOptions()
			options.add_argument("--headless")
			options.add_argument("--log-level=3")
			options.add_experimental_option("excludeSwitches", ["enable-logging"])
			logs_dir = "logs"
			if not os.path.exists(logs_dir):
				os.mkdir(logs_dir)
			log.info("Attaching selenium to driver")
			self.selenium_instance = webdriver.Chrome(executable_path=self.source, options=options,
													  service_log_path=os.path.join(logs_dir, "chromedriver.log"))

	def dispose(self):
		if self.selenium_instance:
			log.info("Shutting down selenium")
			self.selenium_instance.quit()
