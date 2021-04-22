#!/usr/bin/python
import os
import sys
import json
import time
import base64
import datetime
from datetime import date

import yfinance as yf
import pandas as pd
import math

class API():
	def __init__(self):
		self.ClassName	= "StockMarketApi"
		self.Delay 		= 0.2
	
	def CheckForNan(self, value):
		if value == value:
			return True
		return False
	
	def GetStockCurrentPrice(self, ticker):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		price = 0.0
		error = False
		for retry in range(3):
			try:
				objtk = yf.Ticker(ticker)
				time.sleep(self.Delay)
				df_stock = objtk.history(period="1d", interval="5m")
				time.sleep(self.Delay)
				price = "{0:.3f}".format(df_stock["Close"].iloc[-1])
			except Exception as e:
				if retry == 3:
					print("({classname})# [EXCEPTION] GetStockCurrentPrice FAILED {0} {1}".format(ticker,str(e),classname=self.ClassName))
					return True, 0.0
				print("({classname})# [EXCEPTION] GetStockCurrentPrice RETRY [{1}] {0}".format(ticker,retry,classname=self.ClassName))
				
		return error, float(price)
	
	def GetStockInfoRaw(self, ticker):
		objtk = yf.Ticker(ticker)
		time.sleep(self.Delay)
		return objtk.info

	def GetStockInfo(self, ticker):
		objtk = yf.Ticker(ticker)
		time.sleep(self.Delay)

		ask  = 0
		bid  = 0
		high = 0
		low  = 0

		if type(objtk.info["ask"]) == dict:
			ask = objtk.info["ask"]["raw"]
		else:
			ask = objtk.info["ask"]
		
		if type(objtk.info["bid"]) == dict:
			bid = objtk.info["bid"]["raw"]
		else:
			bid = objtk.info["bid"]
		
		if type(objtk.info["dayHigh"]) == dict:
			high = objtk.info["dayHigh"]["raw"]
		else:
			high = objtk.info["dayHigh"]
		
		if type(objtk.info["dayLow"]) == dict:
			low = objtk.info["dayLow"]["raw"]
		else:
			low = objtk.info["dayLow"]

		return {
			"ask": ask,
			"bid": bid,
			"high": high,
			"low": low
		}
	
	def GetStockHistory(self, ticker, period, interval):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		hist = []
		for retry in range(3):
			try:
				objtk = yf.Ticker(ticker)
				time.sleep(self.Delay)
				'''
					Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
					Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
				'''
				data = objtk.history(period=period, interval=interval)
				time.sleep(self.Delay)
				for idx, row in data.iterrows():
					if self.CheckForNan(row['Open']) is False or self.CheckForNan(row['Close']) is False or self.CheckForNan(row['High']) is False or self.CheckForNan(row['Low']) is False:
						continue

					hist.append({
						"date": "{0}".format(idx),
						"open": row['Open'],
						"close": row['Close'],
						"high": row['High'],
						"low": row['Low'],
						"vol": row['Volume']
					})
				return False, hist
			except Exception as e:
				if retry == 3:
					print("({classname})# [EXCEPTION] GetStockHistory {0} {1} {2} FAILED".format(ticker,period,interval,classname=self.ClassName))
					return True, []
				print("({classname})# [EXCEPTION] GetStockHistory RETRY [{3}] {0} {1} {2}".format(ticker,period,interval,retry,classname=self.ClassName))
				time.sleep(0.5)
		return False, hist

	def Get1D(self, ticker):
		return self.GetStockHistory(ticker, "1d", "5m")

	def Get5D(self, ticker):
		return self.GetStockHistory(ticker, "5d", "5m")
	
	def Get1MO(self, ticker):
		return self.GetStockHistory(ticker, "1mo", "1h")
	
	def Get3MO(self, ticker):
		return self.GetStockHistory(ticker, "3mo", "1d")
	
	def Get6MO(self, ticker):
		return self.GetStockHistory(ticker, "6mo", "5d")
	
	def Get1Y(self, ticker):
		return self.GetStockHistory(ticker, "1y", "5d")
	
	def Get2Y(self, ticker):
		return self.GetStockHistory(ticker, "2y", "1wk")
	
	def Get5Y(self, ticker):
		return self.GetStockHistory(ticker, "5y", "1mo")