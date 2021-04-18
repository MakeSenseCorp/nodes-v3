#!/usr/bin/python
import os
import sys
import signal
import json
import time
from urllib.request import urlopen

class Funder():
	def __init__(self, node):
		self.ClassName 	= "Funder"
		self.Node	 	= node
	
	def BindHandler(self):
		# Handlers
		pass

	def GetRequest (self, url, with_dealy):
		try:
			req = urlopen(url, timeout=1)
			if req != None:
				if with_dealy != 0:
					time.sleep(with_dealy)
				data = req.read()
			else:
				return "failed"
		except:
			return "failed"

		return data

	def GetFunderJsonDB(self):
		try:
			data = None
			html = self.GetRequest("https://www.funder.co.il/fundList.aspx", 0).decode()
			rows = html.split("\n")
			# Itterate HTML rows
			for row in rows:
				# Look for "fundlistData"
				if "fundlistData =" in row:
					# Find start of JSON format from string
					index = row.index('=')
					json_str = row[index+1:-2]
					if json_str is not None:
						# Load JSON
						data = json.loads(json_str)["x"]
					return data
		except Exception as e:
			pass
		return None
	
	def GetFundInfoFromDB(self, fund_id):
		try:
			info = None
			data = self.GetRequest("https://www.funder.co.il/fund/{0}".format(fund_id), 1)
			if data is not None:
				html = data.decode()
				rows = html.split("\n")
				# Itterate HTML rows
				for row in rows:
					# Look for "fundHoldingItemsData"
					if "fundHoldingItemsData =" in row:
						# Find start of JSON format from string
						index = row.index('=')
						json_str = row[index+1:-2]
						if json_str is not None:
							info = json.loads(json_str)
						return info
		except Exception as e:
			print("ERROR (GetFundInfoFromDB): Fund id {0} ({1})".format(fund_id,e))
		return None
