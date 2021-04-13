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
import math

from classes import StockMarketAPI
from classes import AlgoMath
from classes import Algos

class StockCalculation():
	def __init__(self):
		self.ClassName 								= "StockCalculation"
		self.BasicPredictionPeriodToIndexMap 		= {
			"1D":  0,
			"5D":  1,
			"1MO": 2,
			"3MO": 3,
			"6MO": 4,
			"1Y":  5
		}
		# Algo
		self.BasicPrediction = Algos.BasicPrediction()
		self.Math 			 = AlgoMath.AlgoMath()

		self.StockSimplePredictionChangeCallback 	= None
	
	def CalculateBasicPrediction(self, stock, period):
		if stock["price"] <= 0:
			print("({classname})# [CalculateBasicPrediction] ({0}) Error: Price not valid for prediction ({1})".format(stock["ticker"],stock["price"],classname=self.ClassName))
			return

		stock_open = []
		for item in stock[period]:
			stock_open.append(item["open"])
		
		try:
			self.BasicPrediction.SetBuffer(stock_open)
			error, output = self.BasicPrediction.Execute()
		
			if error == -1:
				print("OPEN", stock["ticker"], item["open"])
				return
			
			high = output["output"]["index_high"]
			low  = output["output"]["index_low"]
			x 	 = output["output"]["x"]

			index = self.BasicPredictionPeriodToIndexMap[period]
			if x[high] < stock["price"]:
				if "none" in stock["predictions"]["basic"][index]["action"]["current"]:
					stock["predictions"]["basic"][index]["action"]["current"] = "sell"
				else:
					if "sell" not in stock["predictions"]["basic"][index]["action"]["current"]:
						print("({classname})# [CalculateBasicPrediction] ({0}) Prediction changed to SELL {1}".format(stock["ticker"],stock["price"],classname=self.ClassName))
						stock["predictions"]["basic"][index]["action"]["previouse"] = stock["predictions"]["basic"][index]["action"]["current"]
						stock["predictions"]["basic"][index]["action"]["current"] = "sell"
						# Call for update callback
						if self.StockSimplePredictionChangeCallback is not None:
							self.StockSimplePredictionChangeCallback(stock["ticker"], index)
			elif x[low] > stock["price"]:
				if "none" in stock["predictions"]["basic"][index]["action"]["current"]:
					stock["predictions"]["basic"][index]["action"]["current"] = "buy"
				else:
					if "buy" not in stock["predictions"]["basic"][index]["action"]["current"]:
						print("({classname})# [CalculateBasicPrediction] ({0}) Prediction changed to BUY {1}".format(stock["ticker"],stock["price"],classname=self.ClassName))
						stock["predictions"]["basic"][index]["action"]["previouse"] = stock["predictions"]["basic"][index]["action"]["current"]
						stock["predictions"]["basic"][index]["action"]["current"] = "buy"
						# Call for update callback
						if self.StockSimplePredictionChangeCallback is not None:
							self.StockSimplePredictionChangeCallback(stock["ticker"], index)
			else:
				if "none" in stock["predictions"]["basic"][index]["action"]["current"]:
					stock["predictions"]["basic"][index]["action"]["current"] = "hold"
				else:
					if "hold" not in stock["predictions"]["basic"][index]["action"]["current"]:
						print("({classname})# [CalculateBasicPrediction] ({0}) Prediction changed to HOLD {1}".format(stock["ticker"],stock["price"],classname=self.ClassName))
						stock["predictions"]["basic"][index]["action"]["previouse"] = stock["predictions"]["basic"][index]["action"]["current"]
						stock["predictions"]["basic"][index]["action"]["current"] = "hold"
						# Call for update callback
						if self.StockSimplePredictionChangeCallback is not None:
							self.StockSimplePredictionChangeCallback(stock["ticker"], index)
		except Exception as e:
			print("({classname})# [EXCEPTION] (CalculateBasicPrediction) {0} {1}".format(stock["ticker"],str(e),classname=self.ClassName))
		
		return stock

	def GetBasicStatistics(self, data):
		regression_line = []
		close_line = []
		for idx, sample in enumerate(data):
			regression_line.append({
				"y": sample,
				"x": idx
			})
			close_line.append(sample)
			
		var 	 = self.Math.Variance(close_line)
		std 	 = self.Math.Stdev(close_line)
		slope, b = self.Math.CalculateRegression(regression_line)
		r2 		 = self.Math.RValue(regression_line, slope, b)

		return {
			"var": var,
			"std": std,
			"regression": {
				"slope": slope,
				"offset": b,
				"r_value": r2
			}
		}
	
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
		self.Halt 						= False

		self.Algos 						= StockCalculation()
		self.API 						= StockMarketAPI.API()

		# Callbacks
		self.FullLoopPerformedCallback 				= None
		self.StockChangeCallback 					= None
		self.ThresholdEventCallback 				= None
		self.FirstRunDoneCallback 					= None
		self.StockMarketOpenCallback 				= None
		self.StockMarketCloseCallback				= None
		self.StockSimplePredictionChangeCallback 	= None

		# Threading section
		self.ThreadCount				= 10
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

	'''
	def CalculateBasicStatistics(self, data):
		s_min = s_max = s_slope = s_b = s_r2 = s_var = s_std = 0
		warning = False
		if len(data) > 0:
			s_min, s_max 		= self.CalculateMinMax(data)
			s_slope, s_b, s_r2 	= self.GetRegressionLineStatistics(data)
			s_var, s_std 		= self.GetBasicStatistics(data)

			if math.isnan(s_min) is True:
				warning = False
				s_min = 0
			if math.isnan(s_max) is True:
				warning = False
				s_max = 0
			if math.isnan(s_slope) is True:
				warning = False
				s_slope = 0
			if math.isnan(s_b) is True:
				warning = False
				s_b = 0
			if math.isnan(s_r2) is True:
				warning = False
				s_r2 = 0
			if math.isnan(s_var) is True:
				warning = False
				s_var = 0
			if math.isnan(s_std) is True:
				warning = False
				s_std = 0
		else:
			warning = False
		
		return {
			"warning": warning,
			"statistics": {
				"min": float("{0:.2f}".format(s_min)),
				"max": float("{0:.2f}".format(s_max)),
				"slope": float("{0:.2f}".format(s_slope)),
				"std": float("{0:.2f}".format(s_std)),
				"slope_offset": float("{0:.2f}".format(s_b)),
				"r_value": float("{0:.2f}".format(s_r2)),
				"varience": float("{0:.2f}".format(s_var))
			}
		}
	'''
	
	def WaitForMinionsToFinish(self):
		self.LogMSG("({classname})# [WaitForMinionsToFinish]".format(classname=self.ClassName), 5)
		wait_for_all_minions = True
		while wait_for_all_minions is True:
			wait_for_all_minions = False
			for item in self.ThreadPoolStatus:
				if item is True:
					wait_for_all_minions = True
					break
			time.sleep(0.5)
		return

	def StockUpdated(self):
		self.LogMSG("({classname})# [StockUpdated]".format(classname=self.ClassName), 5)
		for ticker in self.CacheDB:
			stock = self.CacheDB[ticker]
			if stock["updated"] is False:
				return False
		return True
	
	def NeedUpdate(self, stock):
		if stock is None:
			return False
		try:
			ts = time.time()
			if stock["updated"] is True:
				vol = stock["1D"][0]["vol"]
				if vol > 1000000:
					return True
				elif vol > 500000:
					if ts - stock["ts_last_updated"] > 5.0:
						return True
				elif vol > 100000:
					if ts - stock["ts_last_updated"] > 10.0:
						return True
				else:
					if ts - stock["ts_last_updated"] > 30.0:
						return True
			else:
				return True
		except Exception as e:
			self.LogMSG("({classname})# [Exeption] NeedUpdate ({0})".format(e,classname=self.ClassName), 5)
		
		return False

	def GetPriceListFromStockPeriod(self, data, p_type):
		prices = []
		if data is not None:
			for item in data:
				prices.append(item[p_type])
		return prices

	def StockMinion(self, index):
		self.LogMSG("({classname})# [MINION] Reporting for duty ({0})".format(index,classname=self.ClassName), 5)
		# Update jobless minons
		self.ThreadPoolLocker.acquire()
		self.JoblessMinions += 1
		self.ThreadPoolLocker.release()
		Interval = 0.25

		algos = StockCalculation()
		algos.StockSimplePredictionChangeCallback = self.StockSimplePredictionChangeCallback
		atock_api = StockMarketAPI.API()

		while self.WorkerRunning is True:
			try:
				item = self.Queues[index].get(block=True,timeout=None)
				# Update pool thread status
				self.ThreadPoolStatus[index] 	= True
				# Initiate working variables
				error  							= False
				ticker 							= item["ticker"]
				stock  							= self.CacheDB[ticker]
				# Print working message
				self.LogMSG("({classname})# [MINION] Update stock ({0}) ({1})".format(index,ticker,classname=self.ClassName), 5)
				# Update local stock DB
				if stock is not None:
					error, stock["price"] = atock_api.GetStockCurrentPrice(ticker) # Get stock price
					if error is True:
						stock["price"] = None
					else:
						error, stock["1D"] = atock_api.Get1D(ticker)	# Get 1 day history
						if error is True:
							stock["1D"] = None
						else:
							algos.CalculateBasicPrediction(stock, "1D")
							stock_prices = self.GetPriceListFromStockPeriod(stock["1D"], "close")
							stock["statistics"]["basic"][0] = algos.GetBasicStatistics(stock_prices)
						error, stock["5D"] = atock_api.Get5D(ticker)	# Get 5 days history
						if error is True:
							stock["5D"] = None
						else:
							algos.CalculateBasicPrediction(stock, "5D")
							stock_prices = self.GetPriceListFromStockPeriod(stock["5D"], "close")
							stock["statistics"]["basic"][1] = algos.GetBasicStatistics(stock_prices)
						error, stock["1MO"] = atock_api.Get1MO(ticker)	# Get 1 month history
						if error is True:
							stock["1MO"] = None
						else:
							algos.CalculateBasicPrediction(stock, "1MO")
							stock_prices = self.GetPriceListFromStockPeriod(stock["1MO"], "close")
							stock["statistics"]["basic"][2] = algos.GetBasicStatistics(stock_prices)
						error, stock["3MO"] = atock_api.Get3MO(ticker)	# Get 3 months history
						if error is True:
							stock["3MO"] = None
						else:
							algos.CalculateBasicPrediction(stock, "3MO")
							stock_prices = self.GetPriceListFromStockPeriod(stock["3MO"], "close")
							stock["statistics"]["basic"][3] = algos.GetBasicStatistics(stock_prices)
						error, stock["6MO"] = atock_api.Get6MO(ticker)	# Get 6 months history
						if error is True:
							stock["6MO"] = None
						else:
							algos.CalculateBasicPrediction(stock, "6MO")
							stock_prices = self.GetPriceListFromStockPeriod(stock["6MO"], "close")
							stock["statistics"]["basic"][4] = algos.GetBasicStatistics(stock_prices)
						error, stock["1Y"] = atock_api.Get1Y(ticker)	# Get 1 year history
						if error is True:
							stock["1Y"] = None
						else:
							algos.CalculateBasicPrediction(stock, "1Y")
							stock_prices = self.GetPriceListFromStockPeriod(stock["1Y"], "close")
							stock["statistics"]["basic"][5] = algos.GetBasicStatistics(stock_prices)
						
						# Calculate price difference bteween today and previouse day
						if stock["1D"] is not None and stock["5D"] is not None:
							today_open = stock["1D"][0]
							for idx, item in enumerate(stock["5D"]):
								if item["date"] == today_open["date"]:
									stock["prev_market_price"] = stock["5D"][idx-1]["close"]

						# Check for thresholds
						for threshold in stock["thresholds"]:
							threshold["activated"] = False
							if threshold["type"] == 1:
								if float(threshold["value"]) > float(stock["price"]):
									threshold["activated"] = True
							elif threshold["type"] == 2:
								if float(threshold["value"]) == float(stock["price"]):
									threshold["activated"] = True
							elif threshold["type"] == 3:
								if float(threshold["value"]) < float(stock["price"]):
									threshold["activated"] = True
							else:
								pass
							
							if threshold["activated"] is True:
								if self.ThresholdEventCallback is not None:
									self.ThresholdEventCallback(ticker, stock["price"], threshold)
						
						if error is True:
							# Stock was not updated correctly
							stock["updated"] = False
						else:
							# Update stock status to updated and update timestamp
							stock["updated"] = True
							stock["ts_last_updated"] 	= time.time()
				# Wait several MS
				time.sleep(Interval)
				# Free to accept new job
				self.ThreadPoolStatus[index] = False
				# Signal master in case he waits on signal
				self.Signal.set()
			except Exception as e:
				# BUG #1 - name 'stock' is not defined
				self.LogMSG("({classname})# [EXCEPTION] MINION {0} {1}".format(index,str(e),classname=self.ClassName), 5)
				stock["updated"] = False
				self.ThreadPoolStatus[index] = False
				self.Signal.set()
	
	def StockMonitorWorker(self):
		self.MarketPollingInterval = 0.5
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
				self.MarketOpen = self.IsMarketOpen()
				if self.Halt is False:
					if self.MarketOpen is True or self.FirstStockUpdateRun is False:
						if self.MarketOpen is False:
							self.MarketPollingInterval = 10
						else:
							self.MarketPollingInterval = 1
						# Itterate over all user stocks
						for ticker in self.CacheDB:
							if self.Halt is True:
								# Get out
								break
							stock 	 = self.CacheDB[ticker]
							# self.LogMSG("({classname})# [MASTER] {0} {1}".format(ticker,stock,classname=self.ClassName), 5)
							d_ticker = ticker
							# Check if stock is not null
							if stock is not None:
								# Check if stock need to be updated
								if self.NeedUpdate(stock) is True:
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
								else:
									pass
							else:
								self.LogMSG("({classname})# [Exception] MASTER Stock {0} is null".format(ticker,classname=self.ClassName), 5)
						if self.FirstStockUpdateRun is False:
							self.WaitForMinionsToFinish()
							if self.FirstRunDoneCallback is not None:
								self.FirstRunDoneCallback()
					if self.FirstStockUpdateRun is False:
						if self.StockUpdated() is True:
							self.FirstStockUpdateRun = True
				time.sleep(self.MarketPollingInterval)
			except Exception as e:
				self.LogMSG("({classname})# [Exeption] MASTER ({0}) ({1})".format(d_ticker,e,classname=self.ClassName), 5)

	def PauseMarket(self):
		self.LogMSG("({classname})# [PauseMarket]".format(classname=self.ClassName), 5)
		self.Halt = True
	
	def ContinueMarket(self):
		self.LogMSG("({classname})# [ContinueMarket]".format(classname=self.ClassName), 5)
		self.Halt = False

	def UpdateStocks(self):
		self.FirstStockUpdateRun = False
	
	def RemoveThreshold(self, ticker, threshold_id):
		self.Locker.acquire()
		try:
			stock = self.CacheDB[ticker]
			threshold = None
			for item in stock["thresholds"]:
				if item["id"] == threshold_id:
					threshold = item
					break
			if threshold is not None:
				del threshold
		except:
			pass
		self.Locker.release()
	
	def RemoveThresholdByStockActionId(self, ticker, act_id):
		self.Locker.acquire()
		try:
			stock = self.CacheDB[ticker]
			threshold_idx = -1
			thresholds = stock["thresholds"]
			for idx, item in enumerate(thresholds):
				if item["stock_action_id"] == act_id:
					threshold_idx = idx
					break
			if threshold_idx != -1:
				del thresholds[threshold_idx]
		except:
			pass
		self.Locker.release()

	def AppendThreshold(self, ticker, threshold):
		self.Locker.acquire()
		try:
			stock = self.CacheDB[ticker]
			threshold["id"] = time.time()
			stock["thresholds"].append(threshold)
		except:
			pass
		self.Locker.release()

	def GenerateEmtpyStock(self):
		return {
			"ticker"			: "",
			"price"				: 0,
			"1D"				: None,
			"5D"				: None,
			"1MO"				: None,
			"3MO"				: None,
			"6MO"				: None,
			"1Y"				: None,
			"updated"			: False,
			"pulled"			: False,
			"ts_last_updated"	: 0,
			"thresholds"		: [],
			"statistics"		: {
				"basic": [
					{
						"std"	: 0.0,
						"var"	: 0.0,
						"regression": {
							"slope": 0.0,
							"offset": 0.0,
							"r_value": 0.0
						}
					},
					{
						"std"	: 0.0,
						"var"	: 0.0,
						"regression": {
							"slope": 0.0,
							"offset": 0.0,
							"r_value": 0.0
						}
					},
					{
						"std"	: 0.0,
						"var"	: 0.0,
						"regression": {
							"slope": 0.0,
							"offset": 0.0,
							"r_value": 0.0
						}
					},
					{
						"std"	: 0.0,
						"var"	: 0.0,
						"regression": {
							"slope": 0.0,
							"offset": 0.0,
							"r_value": 0.0
						}
					},
					{
						"std"	: 0.0,
						"var"	: 0.0,
						"regression": {
							"slope": 0.0,
							"offset": 0.0,
							"r_value": 0.0
						}
					},
					{
						"std"	: 0.0,
						"var"	: 0.0,
						"regression": {
							"slope": 0.0,
							"offset": 0.0,
							"r_value": 0.0
						}
					}
				]
			},
			"predictions": {
				"basic": [
					{
						"action" : {
							"current": "none",
							"previouse": "none"
						},
						"high"	 : 0.0,
						"middle" : 0.0,
						"low"	 : 0.0,
						"action_flags": [0,0,0]
					},
					{
						"action" : {
							"current": "none",
							"previouse": "none"
						},
						"high"	 : 0.0,
						"middle" : 0.0,
						"low"	 : 0.0,
						"action_flags": [0,0,0]
					},
					{
						"action" : {
							"current": "none",
							"previouse": "none"
						},
						"high"	 : 0.0,
						"middle" : 0.0,
						"low"	 : 0.0,
						"action_flags": [0,0,0]
					},
					{
						"action" : {
							"current": "none",
							"previouse": "none"
						},
						"high"	 : 0.0,
						"middle" : 0.0,
						"low"	 : 0.0,
						"action_flags": [0,0,0]
					},
					{
						"action" : {
							"current": "none",
							"previouse": "none"
						},
						"high"	 : 0.0,
						"middle" : 0.0,
						"low"	 : 0.0,
						"action_flags": [0,0,0]
					},
					{
						"action" : {
							"current": "none",
							"previouse": "none"
						},
						"high"	 : 0.0,
						"middle" : 0.0,
						"low"	 : 0.0,
						"action_flags": [0,0,0]
					}
				]
			}
		}
	
	def AppendStock(self, ticker):
		self.Locker.acquire()
		try:
			stock = self.GenerateEmtpyStock()
			stock["ticker"] 				= ticker
			self.CacheDB[stock["ticker"]] 	= stock
			self.FirstStockUpdateRun 		= False
		except:
			pass
		self.Locker.release()
	
	def GetMarketStatus(self):
		res = {
			"local_stock_market_ready": self.FirstStockUpdateRun
		}
		return res

	def GetCacheDB(self):
		return self.CacheDB

	def GetStockInformation(self, ticker):
		self.Locker.acquire()
		try:
			if ticker in self.CacheDB:
				stock = self.CacheDB[ticker]
				self.Locker.release()
				return stock
		except:
			pass
		self.Locker.release()
		return None

	def RemoveStock(self, ticker):
		if ticker in self.CacheDB:
			self.Locker.acquire()
			try:
				del self.CacheDB[ticker]
			except:
				pass
			self.Locker.release()
