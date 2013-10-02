# -*- coding: utf-8 -*-
import requests, re, vobject, time, codecs, getpass
from datetime import datetime

class Logger:
	GET_COOKIES_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/logOutUser.do'
	LOGIN_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/logInUser.do'
	ZAPISY_COOKIES_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/zapisy.do?event=WyborSluchacza'
	ZAPISY_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/zapisy.do?href=#hrefZapisySzczSlu'
	ZAPISY_GUIDE_LINE_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/zapisy.do'
	ZAPISY_GUIDE_LINE_COOKIES_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/zapisy.do?event=WyborSluchacza'
	TERMINY_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/terminyGrupy.do'
	LOGOUT_URL = 'https://edukacja.pwr.wroc.pl/EdukacjaWeb/logOutUser.do'
	
	def __init__(self):
		pass
		
	def login(self, login, password):
		login_data = {'login': login, 'password': password}
		
		token = self._get_token()
		login_data['cl.edu.web.TOKEN'] = token

		login_r = requests.post(self.LOGIN_URL, data=login_data, cookies=self.last_cookie, allow_redirects=True)
		login_r_code = login_r.text.encode('utf-8')
		
		
		if "Brak uprawnień dostępu do żądanego zasobu." in login_r_code:
			raise Exception("invalid login/pass")

		if "Jesteś w tej chwili jednym z kilku tysięcy chętnych do odwiedzenia naszego portalu" in login_r_code:
			raise Exception("server overloaded - huehue")
			
		#set cookie
		self.session = self._parse_session(login_r_code)
		self.last_cookie = login_r.cookies
		self.token = token
		
	def _parse_session(self, code):
		p = re.compile(r'<input type="hidden" name="clEduWebSESSIONTOKEN" value="(?P<session>[a-zA-Z0-9=]+)">')
		m = p.search(code)
		
		if m == None:
			raise Exception("can't complie session")
			
		return m.group('session')
		
	def _parse_token(self, code):

		p = re.compile(r'<input type="hidden" name="cl.edu.web.TOKEN" value="(?P<token>[a-zA-Z0-9=]+)">')
		m = p.search(code)
		
		if m == None:
			raise Exception("can't complie token")
			
		return m.group('token')
		
	def _get_token(self):
		# get session and token
		get_cookies_r = requests.get(self.GET_COOKIES_URL)
		
		token = self._parse_token(get_cookies_r.text.encode('utf-8'))

		# set cookie
		self.last_cookie = get_cookies_r.cookies

		return token
		
	def generate_curses_list(self):
		code = self._get_schedule()
		
		# parse code
		
	def generate_calendar(self):
		code = self._get_schedule()
		
		# parse code
		p = re.compile(r'<td class="BIALA">(?P<id>.*?)</td>', re.DOTALL)
		kursy = []
		for kurs in self._group(p.findall(code), 6):
			course_code = kurs[5].strip().decode('utf-8')[0].upper()
			if course_code == "Z":
				course_code = "L"
			
			kursy.append("[%s] %s" % (course_code, kurs[1].strip().decode('utf-8')))
		
		p = re.compile(r'<input type="hidden" name="grzId" value="(?P<id>[0-9]+)">')
		m = p.findall(code)
		
		# get session and token
		token = self._parse_token(code)
		
		if m == None:
			raise Exception("can't find data")
		
		curses = []
		i=0
		for id in m:
			curses.append({'name': kursy[i],
				'data': self._get_curse_details(id, token, self.session)
			})
			i += 1
		
		# create calendar file
		cal = vobject.iCalendar()
		cal.add('method').value = 'PUBLISH'
		cal.add('calscale').value = 'GREGORIAN'
		cal.add('x-wr-calname').value = 'PLAN PWR'
		cal.add('x-wr-timezone').value = 'Poland/Warsaw'
		cal.add('x-wr-caldesc').value = ''

		for curse_group in curses:
			for curse in self._group(curse_group['data'], 7):
				print curse
				data = curse[1].split('-')
				time_start = curse[2].split(':')
				time_end = curse[3].split(':')

				vevent = cal.add('vevent')
				vevent.add('dtstamp').value = datetime(int(data[0]), int(data[1]), int(data[2]), int(time_start[0]), int(time_start[1]))
				vevent.add('dtstart').value = datetime(int(data[0]), int(data[1]), int(data[2]), int(time_start[0]), int(time_start[1]))
				vevent.add('dtend').value = datetime(int(data[0]), int(data[1]), int(data[2]), int(time_end[0]), int(time_end[1]))
				vevent.add('summary').value = curse_group['name']
				vevent.add('description').value = curse[4].decode('utf-8')
				vevent.add('location').value = "%s / %s" % (curse[5].decode('utf-8'),curse[6].decode('utf-8'))

		
		f = codecs.open('plan.ics', 'w', 'utf-8')
		f.write(cal.serialize().decode('utf-8'))
		f.close()
	def _group(self, lst, n):
		for i in range(0, len(lst), n):
			val = lst[i:i+n]
			if len(val) == n:
				yield tuple(val)
		
	def _get_schedule(self):
		# get schedule
		zapisy_cookies_r = requests.get(self.ZAPISY_GUIDE_LINE_COOKIES_URL, params={'clEduWebSESSIONTOKEN': self.session}, cookies=self.last_cookie)
		zapisy_cookies_html = zapisy_cookies_r.text.encode('utf-8')
		token = self._parse_token(zapisy_cookies_html)

		# check if there is guide line option
		if "(Aktywny)" in zapisy_cookies_html:
			# get id
			p = re.compile(r'<option value="(?P<id>[0-9]+)" selected>')
			m = p.findall(zapisy_cookies_html)
			data = {'ineSluId':m[0], 'event_WyborSluchaczaSubmit':'Wybierz','clEduWebSESSIONTOKEN': self.session, 'cl.edu.web.TOKEN': token}
			guide_line_r = requests.post(self.ZAPISY_GUIDE_LINE_URL, data=data, cookies=self.last_cookie)
			token = self._parse_token(guide_line_r.text.encode('utf-8'))

		zapisy_data = {'clEduWebSESSIONTOKEN': self.session,
			'cl.edu.web.TOKEN': token,
			'event_WyborZapisowWidok': 'Przełącz na <Grupy zajęciowe, do których słuchacz jest zapisany w semestrze>'
		}

		zapisy_r = requests.post(self.ZAPISY_URL, cookies=self.last_cookie, data=zapisy_data, allow_redirects=True)
	
		# set cookie
		self.last_cookie = zapisy_r.cookies
		self.token = token
		
		return zapisy_r.text.encode('utf-8')
		
	def _get_curse_details(self, id, token, session):
		post_data = {'clEduWebSESSIONTOKEN': session,
			'cl.edu.web.TOKEN': token,
			'grzId': id,
			'paramPowrotAction': 'zapisy.do?href=#hrefZapisaneGrupySluchacza',
			'paramPowrotEvent': 'event_SzczegolyGrupyPowrot',
			'paramPowrotButtonBundle': 'zapisy',
			'paramPowrotButtonKey': 'button.terminyGrupy.powrot',
			'event_PokazTerminy': 'Szczegółowy terminarz'
		}
		curse_r = requests.post(self.TERMINY_URL, cookies=self.last_cookie, data=post_data, allow_redirects=True)
	
		# set cookie
		self.last_cookie = curse_r.cookies
		
		# parse code - only next
		p = re.compile(r'<td class="BIALA" align="center" style="background-color: #aafaaa !important;">(?P<data>.*)</td>', re.UNICODE)
		m = p.findall(curse_r.text.encode('utf-8'))
		
		return m
	
	def logout(self):
		post_data = {'clEduWebSESSIONTOKEN': self.session,
			'cl.edu.web.TOKEN': self.token,
			'wyloguj': ''
		}
		
		requests.post(self.LOGOUT_URL, data=post_data, cookies=self.last_cookie, allow_redirects=True)

if __name__ == "__main__":
	login = raw_input("Login: ")
	password = getpass.getpass()
	
	#gogo
	l = Logger()
	l.login(login, password)
	l.generate_calendar()
	l.logout()