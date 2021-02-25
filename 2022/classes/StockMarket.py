#!/usr/bin/python
import os
import sys
import signal
import json
import time
import _thread
import threading
import base64
import datetime
from datetime import date
import queue

import yfinance as yf
import pandas as pd
import math

class StockMarket():
	def __init__(self):
		self.ClassName					= "StockMarket"
		self.CacheDB 					= {}
		self.WorkerRunning 				= False
		self.Locker						= threading.Lock()
		self.FirstStockUpdateRun 		= False
		self.MarketOpen 				= False
		self.MarketPollingInterval 		= 1
		self.Logger						= None

		self.FullLoopPerformedCallback 	= None

		# Threading section
		self.ThreadCount				= 5
		self.Signal 					= threading.Event()
		self.Queues		    			= []
		self.ThreadPool 				= []
		self.ThreadPoolStatus 			= []
		self.ThreadPoolLocker			= threading.Lock()
		self.JoblessMinions 			= 0

		# Init thread minion queues
		self.Signal.set()
		for idx in range(self.ThreadCount):
			self.Queues.append(queue.Queue())
	
	def SetLogger(self, logger):
		self.Logger	= logger

	def LogMSG(self, message, level):
		if self.Logger is not None:
			self.Logger.Log(message, level)
		else:
			print("({classname})# [NONE LOGGER] - {0}".format(message,classname=self.ClassName))
	
	def Start(self):
		self.WorkerRunning = True
		self.LogMSG("({classname})# Start".format(classname=self.ClassName), 5)
		_thread.start_new_thread(self.StockMonitorWorker, ())

	def Stop(self):
		self.WorkerRunning = False
		self.LogMSG("({classname})# Stop".format(classname=self.ClassName), 5)
	
	def IsMarketOpen(self):
		currTime = datetime.datetime.now().time()
		return (currTime > datetime.time(16,25) and currTime < datetime.time(23,5))
	
	def StockMinion(self, index):
		self.LogMSG("({classname})# [MINION] Reporting for duty ({0})".format(index,classname=self.ClassName), 5)
		# Update jobless minons
		self.ThreadPoolLocker.acquire()
		self.JoblessMinions += 1
		self.ThreadPoolLocker.release()

		while self.WorkerRunning is True:
			try:
				item = self.Queues[index].get(block=True,timeout=None)
				self.ThreadPoolStatus[index] = True
				ticker = item["ticker"]
				stock = self.CacheDB[ticker]
				self.LogMSG("({classname})# [MINION] Update stock ({0}) ({1})".format(index,ticker,classname=self.ClassName), 5)
				# Update local stock DB
				stock["1D"]					= self.Get1D(ticker)
				stock["5D"] 	 			= self.Get5D(ticker)
				stock["1MO"] 	 			= self.Get1MO(ticker)
				stock["price"] 	 			= self.GetStockCurrentPrice(ticker)
				stock["updated"] 			= True
				stock["ts_last_updated"] 	= time.time()
				# Free to accept new job
				self.ThreadPoolStatus[index] = False
				# Signal master in case he waits on signal
				self.Signal.set()
			except Exception as e:
				self.LogMSG("({classname})# [EXCEPTION] MINION {0} {1}".format(index,str(e),classname=self.ClassName), 5)
				self.ThreadPoolStatus[index] = False
				self.Signal.set()
	
	def StockMonitorWorker(self):
		self.MarketPollingInterval = 0
		# Start your minions
		for idx in range(self.ThreadCount):
			self.ThreadPoolStatus.append(False)
			self.LogMSG("({classname})# [MASTER] Minion ({0}) report for duty".format(idx,classname=self.ClassName), 5)
			self.ThreadPool.append(_thread.start_new_thread(self.StockMinion, (idx,)))
		
		# Wait untill minions will report for duty
		while self.JoblessMinions < self.ThreadCount:
			time.sleep(1)

		d_ticker = ""
		while self.WorkerRunning is True:
			try:
				self.MarketOpen = False # self.IsMarketOpen()
				if self.MarketOpen is True or self.FirstStockUpdateRun is False:
					for ticker in self.CacheDB:
						stock = self.CacheDB[ticker]
						d_ticker = ticker
						ts = time.time()
						if stock["updated"] is True:
							vol = stock["1D"][0]["vol"]
							if vol > 1000000:
								stock["updated"] = False
							elif vol > 500000:
								if ts - stock["ts_last_updated"] > 5.0:
									stock["updated"] = False
							elif vol > 100000:
								if ts - stock["ts_last_updated"] > 10.0:
									stock["updated"] = False
							else:
								if ts - stock["ts_last_updated"] > 30.0:
									stock["updated"] = False
						
						# Find free queue
						jobless_minion_found = False
						while jobless_minion_found is False:
							for idx, item in enumerate(self.ThreadPoolStatus):
								if item is False:
									# Send job to minion
									self.Queues[idx].put({
										"ticker": ticker
									})
									time.sleep(0.1)
									jobless_minion_found = True
									break
							if jobless_minion_found is False:
								# self.LogMSG("({classname})# [MASTER] Wait...".format(classname=self.ClassName), 5)
								self.Signal.clear()
								# free minion not found, wait
								self.Signal.wait()
					self.FirstStockUpdateRun = True
			except Exception as e:
				self.LogMSG("({classname})# [Exeption] MASTER ({0}) ({1})".format(d_ticker,e,classname=self.ClassName), 5)

	def AppendStock(self, stock):
		self.Locker.acquire()
		try:
			stock["ts_last_updated"] 		= 0
			self.CacheDB[stock["ticker"]] 	= stock
		except:
			pass
		self.Locker.release()
	
	def GetMarketStatus(self):
		res = {
			"local_stock_market_ready": self.FirstStockUpdateRun
		}
		return res

	def GetStocks(self):
		return self.CacheDB

	def GetStockInformation(self, ticker):
		try:
			if ticker in self.CacheDB:
				stock = self.CacheDB[ticker]
				return stock
		except:
			pass
		return None

	def RemoveStock(self, ticker):
		if ticker in self.CacheDB:
			self.Locker.acquire()
			try:
				del self.CacheDB[ticker]
			except:
				pass
			self.Locker.release()
	
	def GetStockCurrentPrice(self, ticker):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		try:
			objtk = yf.Ticker(ticker)
			df_stock = objtk.history(period="1d", interval="5m")
			price = "{0:.3f}".format(df_stock["Close"].iloc[-1])
		except:
			price = "0"
		return float(price)
	
	def GetStockInfoRaw(self, ticker):
		objtk = yf.Ticker(ticker)
		return objtk.info

	def GetStockInfo(self, ticker):
		objtk = yf.Ticker(ticker)

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
	
	def GetStock(self, ticker, period, interval):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		hist = []
		objtk = yf.Ticker(ticker)
		'''
			Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
			Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
		'''
		data = objtk.history(period=period, interval=interval)
		for idx, row in data.iterrows():
			hist.append({
				"date": "{0}".format(idx),
				"open": row['Open'],
				"close": row['Close'],
				"high": row['High'],
				"low": row['Low'],
				"vol": row['Volume']
			})
		return hist

	def Get1D(self, ticker):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		hist = []
		objtk = yf.Ticker(ticker)
		data = objtk.history(period="1d", interval="5m")
		for idx, row in data.iterrows():
			hist.append({
				"date": "{0}".format(idx).replace("00:00:00",""),
				"open": row['Open'],
				"close": row['Close'],
				"high": row['High'],
				"low": row['Low'],
				"vol": row['Volume']
			})
		return hist

	def Get5D(self, ticker):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		hist = []
		objtk = yf.Ticker(ticker)
		data = objtk.history(period="5d", interval="5m")
		for idx, row in data.iterrows():
			hist.append({
				"date": "{0}".format(idx).replace("00:00:00",""),
				"open": row['Open'],
				"close": row['Close'],
				"high": row['High'],
				"low": row['Low'],
				"vol": row['Volume']
			})
		return hist
	
	def CreateHistogram(self, buffer, hist_bin_size):
		ret_hist_buffer_y = []
		ret_hist_buffer_x = []
		try:
			hist_len = len(buffer)
			hist_buffer_y = []
			hist_buffer_x = []
			if hist_len > 0:
				pmax = 0		
				pmin = buffer[0]
				for item in buffer:
					if pmax < item:
						pmax = item
					if pmin > item:
						pmin = item
				normal = 1.0 / (pmax - pmin)

				hist_buffer_y = [0]*hist_len # [0]*(int(pmax - pmin) + 2)
				hist_buffer_x = [0]*hist_len
				for sample in buffer:
					index = int((sample-pmin)*normal*hist_len) - 1
					#print(hist_len,index)
					hist_buffer_y[index] += 1
					hist_buffer_x[index] = float("{0:.3f}".format(sample))
				
				for idx, sample in enumerate(hist_buffer_y):
					if sample > 0:
						ret_hist_buffer_y.append(sample)
						ret_hist_buffer_x.append(hist_buffer_x[idx])
		except:
			pass
		return ret_hist_buffer_y, ret_hist_buffer_x

	def Get1MO(self, ticker):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		hist = []
		objtk = yf.Ticker(ticker)
		data = objtk.history(period="1mo")
		for idx, row in data.iterrows():
			hist.append({
				"date": "{0}".format(idx),
				"open": row['Open'],
				"close": row['Close'],
				"high": row['High'],
				"low": row['Low'],
				"vol": row['Volume']
			})
		return hist
	
	def CalculateMinMax(self, data):
		pmax = 0
		pmin = 0
		if len(data) > 0:
			pmin = data[0]["close"]
			for item in data:
				if pmax < item["close"]:
					pmax = item["close"]
				if pmin > item["close"]:
					pmin = item["close"]
		return pmin, pmax

	def CalculateRegression(self, coordinates):
		avg_x = 0
		avg_y = 0
		x_dist_2_sum = 0
		y_dist_2_sum = 0
		# Calculate avgs
		for sample in coordinates:
			avg_x += sample["x"]
			avg_y += sample["y"]
			
		avg_x = (avg_x) / (len(coordinates))
		avg_y = (avg_y) / (len(coordinates))

		for sample in coordinates:
			sample["x_dist"] = sample["x"] - avg_x
			sample["y_dist"] = sample["y"] - avg_y

			sample["x_dist_2"] = sample["x_dist"] * sample["x_dist"]
			sample["y_dist_2"] = sample["x_dist"] * sample["y_dist"]

			x_dist_2_sum += sample["x_dist_2"]
			y_dist_2_sum += sample["y_dist_2"]
		
		if x_dist_2_sum <= 0:
			return 0, 0
		
		slope = (y_dist_2_sum) / (x_dist_2_sum)
		b = avg_y - slope * avg_x

		return slope, b
		
	def RValue(self, coordinates, slope, b):
		avg_y = 0
		y_dist_2_sum = 0
		estimated_y_dist_2_sum = 0
		# Calculate avgs
		for sample in coordinates:
			avg_y += sample["y"]
		avg_y = float(avg_y) / float(len(coordinates))

		for sample in coordinates:
			sample["y_dist"] = sample["y"] - avg_y
			sample["y_dist_2"] = sample["y_dist"] * sample["y_dist"]
			sample["estimated_y"] = sample["x"] * slope + b
			sample["estimated_y_dist"] = sample["estimated_y"] - avg_y
			sample["estimated_y_dist_2"] = sample["estimated_y_dist"] * sample["estimated_y_dist"]
			y_dist_2_sum += sample["y_dist_2"]
			estimated_y_dist_2_sum += sample["estimated_y_dist_2"]
		
		if float(y_dist_2_sum) <= 0.0:
			return 0.0
		
		r = float(estimated_y_dist_2_sum) / float(y_dist_2_sum)
		return r

	def Variance(self, data, ddof=0):
		n = len(data)
		mean = sum(data) / n
		return sum((x - mean) ** 2 for x in data) / (n - ddof)

	def Stdev(self, data):
		var = self.Variance(data)
		std_dev = math.sqrt(var)
		return std_dev

	def GetRegressionLineStatistics(self, data):
		line = []
		for idx, item in enumerate(data):
			line.append({
				"y": item["close"],
				"x": idx
			})
		
		slope, b = self.CalculateRegression(line)
		r2 = self.RValue(line, slope, b)
		return slope, b, r2

	def GetBasicStatistics(self, data):
		line = []
		for item in data:
			line.append(item["close"])
		var = self.Variance(line)
		std = self.Stdev(line)
		return var, std
