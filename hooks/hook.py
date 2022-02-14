from datetime import datetime

from utils.log import Log as log
import requests


class Hook:
	def __init__(self, name, config, grades):
		self.grades = grades
		self.failed = False
		if name == 'discord':
			self._init_discord(config['hooks']['discord']['webhook_url'])
		elif name == 'telegram':
			self._init_telegram(config['hooks']['telegram']['token'], config['hooks']['telegram']['chat_id'])
		else:
			raise ValueError('unknown hook: %s' % name)

	def format(self):
		if self.failed: return
		if self.name == 'discord':
			return self._format_discord()
		elif self.name == 'telegram':
			return self._format_telegram()
		else:
			raise ValueError('unknown hook: %s' % self.name)

	def notify(self, s):
		if self.failed: return
		if self.name == 'discord':
			return self._notify_discord(s)
		elif self.name == 'telegram':
			return self._notify_telegram(s)
		else:
			raise ValueError('unknown hook: %s' % self.name)

	def _init_discord(self, url):
		if len(url) == 0:
			self.failed = True
			log.warn('Skipping discord hook as no webhook url was specified')
			return
		self.name = 'discord'
		self.webhook_url = url

	def _init_telegram(self, token, chat_id):
		if len(token) == 0 or len(chat_id) == 0:
			self.failed = True
			log.warn('Skipping telegram hook as no token/chat_id was specified')
			return
		self.name = 'telegram'
		self.token = token
		self.chat_id = chat_id

	def _format_discord(self):
		if self.failed: return
		fields = []
		for k, v in self.grades.items():
			field = {'name': f'**{k}** ', 'value': ''}
			for kk, vv in v.items():
				if len(vv) > 0:
					field['value'] += f"{kk.capitalize().ljust(6, '᲼')} : {' '.join([f'` {w} `' for w in vv])}\n"
			fields.append(field)
		return fields

	def _format_telegram(self):
		if self.failed: return
		s = "Vous avez reçu de nouvelles notes sur GAPS !\n"
		for k, v in self.grades.items():
			s += f"**{k}**:\n"
			for kk, vv in v.items():
				if len(vv) > 0:
					s += f"{kk.capitalize().ljust(6, ' ')} : {', '.join([f'` {w} `' for w in vv])}\n"
		return s

	def _notify_discord(self, f):
		if self.failed: return
		payload = {
			"embeds": [{
				"title": "Automatic GAPS",
				"color": 16777215,
				"description": 'Vous avez reçu de nouvelles notes sur GAPS !',
				"fields": f,
				"thumbnail": {
					"url": 'https://gaps.heig-vd.ch/img/banner.png'
				},
				"timestamp": str(datetime.now())
			}]
		}
		res = requests.post(self.webhook_url, json=payload)
		if res.status_code < 400:
			log.success('Successfully notified new grades on discord')
		else:
			log.err('Failed to notify new grades on discord, error: ' + str(res.status_code))

	def _notify_telegram(self, s):
		if self.failed: return
		request_url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={s}&parse_mode=markdown"
		res = requests.get(request_url)
		if res.status_code < 400:
			log.success('Successfully notified new grades on Telegram')
		else:
			log.err('Failed to notify new grades on Telegram, error: ' + str(res.status_code))
