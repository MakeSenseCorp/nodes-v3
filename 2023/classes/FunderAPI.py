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
		retry = 0
		while retry < 3:
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
				break
			except Exception as e:
				retry += 1
		return None
	
	def GetFundInfoFromDB(self, fund_id):
		info = None
		retry = 0
		while retry < 3:
			try:
				data = self.GetRequest("https://www.funder.co.il/fund/{0}".format(fund_id), 1)
				if data is not None:
					info = {
						"holdings": None,
						"graph": None,
						"info": None
					}
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
								info["holdings"] = json.loads(json_str)
						elif "fundGraphData =" in row:
							# Find start of JSON format from string
							index = row.index('=')
							json_str = row[index+1:-2]
							if json_str is not None:
								info["graph"] = json.loads(json_str)
						elif "fundData =" in row:
							# Find start of JSON format from string
							index = row.index('=')
							json_str = row[index+1:-2]
							if json_str is not None:
								info["info"] = json.loads(json_str)
						else:
							pass
					break
			except Exception as e:
				print("ERROR (GetFundInfoFromDB): Fund id {0} ({1})".format(fund_id,e))
				retry += 1
				info = None
		return info

'''
5130315
https://www.funder.co.il/wsfund.asmx/GetFundTickerm?callback=jQuery111306779790886268987_1621159388408&id=5130315&startDate=2018-05-16&endDate=2021-05-17&_=1621159388411
https://www.funder.co.il/wsfund.asmx/GetFundTickerm?callback=jQuery&id=[FUND_NUMBER]&startDate=2018-05-16&endDate=2021-05-17&_=[SIMPLE_NUMBER]
'''
