#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ToDO:  投稿にキューを使う？、明らかに絵文字じゃないのを除外する、
#           時報は別ファイルにする
#

import datetime
import sys
import os
import random

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, util
from django.utils import simplejson

ROOT_PATH = os.path.dirname(__file__)
DEBUG = ROOT_PATH.find('/base') != 0

TWITTER_CONSUMER_KEY = 'YOUR_KEY'
TWITTER_CONSUMER_SECRET = 'YOUR_SECRET'
TWITTER_ACCESS_TOKEN = 'YOUR_TOKEN'
TWITTER_ACCESS_TOKEN_SECRET =  'YOUR_TOKEN_SECRET'

SU = ['fukayatsu']
DEBUG_FLG = "macheri_bot debug mode"
RELEASE_FLG = "macheri_bot release mode"

since_param=None
since_id = 0
mode=DEBUG_FLG

class MainPage(webapp.RequestHandler):
	def get(self, arg):
		global mode
		if arg == 'debug':
			#mode = DEBUG_FLG
			self.response.out.write(mode)
		elif arg == 'release':
			mode = RELEASE_FLG
			self.response.out.write(mode)
		else:
			self.response.out.write(mode)


#every minute

class TweetHandler(webapp.RequestHandler):
	def get(self):

		self.response.out.write("<html><head>")
		self.response.out.write('<meta http-equiv="Content-Type" content="text/html"; charset=UTF-8" />')
		self.response.out.write("</head><body><h2>"+mode+"</h2>")
		self.response.out.write("<img src=https://chart.googleapis.com/chart?chst=d_fnote_title&chld=sticky_y|1|004400|l|(%C2%B4%EF%BD%A5%CF%89%EF%BD%A5`)||macheri_bot>")
		global since_id, since_str, mode
		import xml.etree.ElementTree as ET

		#--------------
		#  時報的なもの
		#--------------
		today = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
		hour = today.hour
		minute = today.minute
		day = today.day
		month = today.month

		if minute == 0:
			param = None

			if hour == 0 and day == 7 and month == 6:
				param = {'status': u'@macheri67 (*≧∇≦)ﾉ＜ﾊｯﾋﾟｰﾊﾞｰｽﾃﾞｰ♪ #macheri_happy_birthday'}
			elif hour == 6:
				param = {'status': u"起ｷﾁｬｯﾀﾃﾞｰｽヾ(;｀Д´)ﾉ #macheri_okiro"}
			elif hour == 7:
				param = {'status': u"朝ご飯ﾏﾀﾞｧ?(・∀・ )っ/凵⌒☆ﾁﾝﾁﾝ"}
			elif hour == 12:
				param = {'status': u"お昼ご飯ﾏﾀﾞｧ?(・∀・ )っ/凵⌒☆ﾁﾝﾁﾝ"}
			elif hour == 18:
				param = {'status': u"晩ご飯ﾏﾀﾞｧ?(・∀・ )っ/凵⌒☆ﾁﾝﾁﾝ"}
			elif hour == 0:
				param = {'status': u"眠ｲﾃﾞｰｽヾ(;｀Д´)ﾉ #macheri_nero"}
			elif hour > 6:
				param = {'status': u"＜●＞＜●＞ﾊﾟｯ         "+str(hour)+u"時"}
			else :
				param = {'status': u"(´-ω-`)zzZ    "+str(hour)+u"..  時...ﾑﾆｬ"}
			if mode==RELEASE_FLG:
				statuses_update(param)
		else:
			#--------------
			#  自分のTL解析
			#--------------
			timeline_url = "http://twitter.com/statuses/home_timeline.xml"
			param = None
			if since_id != 0 :
				param = {'since_id': since_id}
			response = make_req(param, timeline_url)

			#since_idの確認
			et = ET.fromstring(response.content)
			statuses = et.findall("status")
			for status in statuses:
				id=long(status.findtext("id"))
				if id > since_id:	#since_idの更新
					since_id = id

			et = ET.fromstring(response.content)
			statuses = et.findall("status")
			self.response.out.write("<h2>"+str(since_id)+"</h2>")

			for status in statuses:
				text = status.find("text").text
				t = text.split(' ')
				id=long(status.findtext("id"))
				user = status.find("user")
				user_id=long(user.findtext("id"))
				screen_name = user.findtext("screen_name")
				in_reply_to_screen_name = status.findtext("in_reply_to_screen_name")

				param = None

				#TL条件分け
				if screen_name == 'macheri_bot':
					self.response.out.write(u"<h2>自分</h2>")
					#自分の発言 何もしない？
					1+1
				elif t[0] == '@macheri_bot':
					#自分宛のリプライ
					if len(t) >=2:
						if (t[1] == 'do') and (screen_name in SU):
							if len(t) >=3:
								if t[2]=='test':
									self.response.out.write(u"<h2>てすと(`･ω･´)</h2>")
									param = {'status': u"てすと(`･ω･´)"}
								elif (t[2]=='release') and (since_id != 0):
									mode=RELEASE_FLG
								elif t[2]=='debug':
									mode=DEBUG_FLG
								elif t[2]=='nero':
									1+1
								elif t[2]=='okiro':
									1+1
						else:
							#返信するときは in_reply_to_status_id も設定
							if user_id == 72836317:	#onuki
								m_status = "@"+screen_name+u" (((;｀Д´)))シャー"
							else :
								m_status = "@"+screen_name+u" 呼んだ？(`･ω･´)"
							self.response.out.write(m_status)
							param = {'status': m_status, 'in_reply_to_status_id': id}#'in_reply_to_user_id': user_id
				elif text.find("@macheri_bot")!= -1:
					#メンション?
					self.response.out.write(u"<h2>(´･ω･`)！?</h2>")
					param = {'status': u" (´･ω･`)！？"}
					1+1

				else:
					#その他のTL
					#酒とか、
					word = find_word(text)
					kao = find_kao(text)
					if word != "":
						#ワードに対して反応を
						self.response.out.write(u"<h2>"+word+"</h2>")
						param = {'status': word}
					elif kao != "":
						#顔文字っぽいものを投稿
						self.response.out.write(u"<h2>"+kao+"</h2>")
						param = {'status': kao}
				#paramがNoneじゃなかったら発言
				if param is not None:
					if mode==RELEASE_FLG:
						statuses_update(param)
					elif mode == DEBUG_FLG:
						self.response.out.write('post<br/>')
				else:
					for i in t:
						self.response.out.write(i+", ")
					self.response.out.write("<br/>")

			self.response.out.write("</html></body>")
			mode = RELEASE_FLG

#manual tweet test
class ManualTweetHandler(webapp.RequestHandler):
	def get(self):
		param = {'status': u"＜●＞＜●＞ﾊﾟｯ"}
		statuses_update(param)
		self.response.out.write('post ok')

#ｇｍ
class GrowTweetHandler(webapp.RequestHandler):
	def get(self):
		f = open('tweets.txt')
		data1 = f.read()
		f.close()
		lines1 = data1.split('\n')
		#print type(lines1)
		tweets = []
		for line in lines1:
			tweets.append(line)

		tweet = random.choice(tweets)
		param = {'status': tweet}
		statuses_update(param)
		#self.response.out.write(tweet)

#manual tweet test
class MTHandler(webapp.RequestHandler):
	def get(self):
		s = self.request.get('s')
		if(s!=""):
			param = {'status': s}
			statuses_update(param)
			self.response.out.write("posted:"+s)

#api制限を表示する
class LimitHandler(webapp.RequestHandler):
	def get(self):
		import oauth
		client = oauth.TwitterClient(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET, None)

		result = client.make_request('http://twitter.com/account/rate_limit_status.xml',
			token=TWITTER_ACCESS_TOKEN,
			secret=TWITTER_ACCESS_TOKEN_SECRET,
			protected=True)
		self.response.out.write(result.content)

def statuses_update(param):
	import oauth
	global since_param
	import xml.etree.ElementTree as ET

	result = None
	if (param != since_param) and (param != None):
		since_param = param
		client = oauth.TwitterClient(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET, None)

		for i in range(0, 100):
			result = client.make_request('http://twitter.com/statuses/update.xml',
				token=TWITTER_ACCESS_TOKEN,
				secret=TWITTER_ACCESS_TOKEN_SECRET,
				additional_params=param,
				protected=True,
				method='POST')

			et = ET.fromstring(result.content)
			msg = et.findtext('error')
			if msg=='Status is a duplicate.':
				param['status'] += '.'
			else :
				break

	return result

def make_req(param, api_url):
	import oauth
	client = oauth.TwitterClient(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET, None)

	if param is None:
		response = client.make_request(url=api_url,
			token=TWITTER_ACCESS_TOKEN,
			secret=TWITTER_ACCESS_TOKEN_SECRET)
	else:
		response = client.make_request(url=api_url,
			token=TWITTER_ACCESS_TOKEN,
			secret=TWITTER_ACCESS_TOKEN_SECRET,
				additional_params=param)
	return response

def find_kao(text):
	pair = ( '(' , ')' ), ( u'（', u'）'), (u'／',u'＼'), (u'＼', u'／')

	kao = ""
	for p in pair:
		a = text.find(p[0])
		b = text.rfind(p[1])
		if (a != b) and ((b-a)<15):
			kao = text[a:(b+1)]
	return kao

def find_word(text):
	pair = (u'おえっぷ',u'おえっぷ'),(u'カラオケ',u'カラオケヾ(*´∀｀*)ﾉ')

	word = ""
	for p in pair:
		if(text.find(p[0]) > -1):
			word = p[1]
	return word

def main():
	application = webapp.WSGIApplication([('/tweet', TweetHandler),
		('/limit', LimitHandler),
		('/manual_tweet',ManualTweetHandler),
		('/grow', GrowTweetHandler),
		('/mt',MTHandler),
		('/(.*)', MainPage)
		],debug=DEBUG)
	util.run_wsgi_app(application)

if __name__ == '__main__':
  main()