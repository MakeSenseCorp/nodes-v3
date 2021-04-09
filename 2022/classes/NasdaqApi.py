#!/usr/bin/python
import os
import sys
import signal
import json
import time
import urllib.request
import requests

class Nasdaq():
	def __init__(self, node):
		self.ClassName 	= "Nasdaq"
		self.Node	 	= node
		self.Headers 	= {
			"authority":"www.nasdaq.com",
			"method":"GET",
			"path":"/api/calendar/upcoming",
			"scheme":"https",
			"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"accept-encoding":"gzip, deflate, br",
			"accept-language":"en-GB,en-US;q=0.9,en;q=0.8",
			"cache-control":"max-age=0",
			"sec-fetch-dest":"document",
			"sec-fetch-mode":"navigate",
			"sec-fetch-site":"same-origin",
			"sec-fetch-user":"?1",
			"upgrade-insecure-requests":"1",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
		}
	
	def BindHandler(self):
		# Handlers
		self.Node.ApplicationRequestHandlers['get_nasdaq_events'] = self.GetNasdaqEventsHandler
	
	def GetNasdaqEventsHandler(self, sock, packet):
		payload = self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetNasdaqEventsHandler] {0}".format(payload,classname=self.ClassName),5)
		data = None
		try:
			event = payload["event"]
			if "upcomming" in event:
				data = self.UpcommingEvents()
			elif "recent-articles" in event:
				data = self.RecentArticles(5)
		except Exception as e:
			self.Node.LogMSG("({classname})# [EXCEPTION] GetNasdaqEventsHandler {0} {1}".format(payload,str(e),classname=self.ClassName), 5)

		return {
			"event": payload["event"],
			"data": data
		}
	
	def UpcommingEvents(self):
		# json = urllib.request.urlopen("https://api.nasdaq.com/api/calendar/upcoming")
		json_t = None
		try:
			self.Headers["path"] = "/api/calendar/upcoming"
			response = requests.request('GET', "https://api.nasdaq.com/api/calendar/upcoming", json={}, headers=self.Headers)
			json_t = json.loads(response.text)
		except Exception as e:
			print("({classname})# [EXCEPTION] (UpcommingEvents) {0}".format(str(e),classname=self.ClassName))
		return json_t
	
	def RecentArticles(self, count):
		json_t = None
		try:
			self.Headers["path"] = "/api/v1/recent-articles/undefined/{0}".format(count)
			response = requests.request('GET', "https://www.nasdaq.com//api/v1/recent-articles/undefined/5", json={}, headers=self.Headers)
			json_t = json.loads(response.text)
		except Exception as e:
			print("({classname})# [EXCEPTION] (RecentArticles) {0}".format(str(e),classname=self.ClassName))
		return json_t