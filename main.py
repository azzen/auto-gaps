import toml
import driver.driver as drv
import gaps.gaps as g
from utils.log import Log as log
import json

if __name__ == '__main__':
	with open('config.toml', 'r') as f:
		cfg = toml.load(f)

	driver = drv.WebDriverConfig(cfg)
	try:
		if driver.check_driver_availability():
			driver.attach_selenium()
			gaps = g.Gaps(driver.selenium_instance, cfg)
			gaps.connect()
			grades = gaps.get_grades()
			res, delta = gaps.compare_grades(grades)
			if res == -1:
				gaps.save(grades)
			elif res == 0:
				log.info('No new grade found')
			elif res == 1:
				log.info('Found new grades')
				gaps.save(grades)
				gaps.notify(delta)
	finally:
		driver.dispose()








