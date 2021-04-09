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

class AlgoMath():
	def __init__(self):
		self.ClassName = "AlgoMath"
	
	def FindBufferMaxMin(self, buffer):
		pmax = 0		
		pmin = 0
		if len(buffer) > 0:
			pmin = buffer[0]
			for item in buffer:
				if pmax < item:
					pmax = item
				if pmin > item:
					pmin = item
		return pmin, pmax

	def CreateHistogram(self, buffer, bin_size):
		ret_hist_buffer_y = []
		ret_hist_buffer_x = []
		freq = 1
		try:
			if len(buffer) > 0:
				# Find min and max for this buffer
				pmin, pmax = self.FindBufferMaxMin(buffer)
				# Calculate freq
				freq = (float(pmax) - float(pmin)) / float(bin_size)
				if freq == 0:
					return 0, [pmin], [pmax]
				# Generate x scale
				ret_hist_buffer_x = [(x * freq) + pmin for x in range(0, bin_size)]
				ret_hist_buffer_y = [0] * bin_size
				# Generate y scale
				for sample in buffer:
					index = int((float(sample) - float(pmin)) / freq)
					if index == 25:
						index = 24
					#print(index, sample, freq, pmin, pmax)
					ret_hist_buffer_y[index] += 1
		except Exception as e:
			print("Histograme exception {0}".format(e))
			return 1, [], []
		return 0, ret_hist_buffer_y, ret_hist_buffer_x
	
	def CalculatePercentile(self, low, high, histogram):
		low_perc  			= 0
		low_perc_found  	= False

		mid_perc 			= 0
		mid_perc_found 		= False

		high_perc 			= 0
		high_perc_found 	= False

		pmin 				= 0
		pmin_found 			= False
	
		pmax 				= 0
		pmax_found 			= False

		perc_integral 		= 0.0
		hist_sum 			= 0.0

		hist_len 			= len(histogram)

		for sample in histogram:
			hist_sum += sample

		# TODO - use liniar interpulation
		for idx, sample in enumerate(histogram):
			perc_integral += sample
			if low_perc_found is False:
				if (perc_integral / hist_sum) > low:
					low_perc_found = True
					low_perc = idx
			if high_perc_found is False:
				if (perc_integral / hist_sum) > high:
					high_perc_found = True
					high_perc = idx
			if mid_perc_found is False:
				if (perc_integral / hist_sum) >= 0.5:
					mid_perc_found = True
					mid_perc = idx
			if pmin_found is False:
				if sample > 0:
					pmin_found = True
					pmin = idx
			if pmax_found is False:
				if histogram[(hist_len - 1) - idx] > 0:
					pmax_found = True
					pmax = (hist_len - 1) - idx
		
		return pmin, low_perc, mid_perc, high_perc, pmax

class AlgoBasicPrediction():
	def __init__(self):
		self.ClassName 				= "AlgoBasicPrediction"
		self.Math 					= AlgoMath()
		self.HistogramWindowSize 	= 25
		self.PercentileLow 			= 0.15
		self.PercentileHigh 		= 0.85
		self.Buffer 				= None
	
	def SetBuffer(self, buffer):
		self.Buffer = buffer
	
	def Execute(self):
		error, Y, X = self.Math.CreateHistogram(self.Buffer, self.HistogramWindowSize)
		if error != 0 or len(X) == 0:
			return -1, {
				"output": {
					"x"				: [],
					"y"				: [],
					"index_min"		: 0,
					"index_low"		: 0,
					"index_middle"	: 0,
					"index_high"	: 0,
					"index_max"		: 0
				}
			}
		
		idxMIN, idxLOW, idxMID, idxHIGH, idxMAX = self.Math.CalculatePercentile(self.PercentileLow, self.PercentileHigh, Y)

		return 0, {
			"output": {
				"x"				: X,
				"y"				: Y,
				"index_min"		: idxMIN,
				"index_low"		: idxLOW,
				"index_middle"	: idxMID,
				"index_high"	: idxHIGH,
				"index_max"		: idxMAX
			}
		}

class StockCalculation():
	def __init__(self):
		self.ClassName 								= "StockCalculation"
		self.BasicPredictionPeriodToIndexMap 		= {
			"1D":  0,
			"5D":  1,
			"1MO": 2,
			"3MO": 3,
			"6MO": 4
		}
		# Algo
		self.BasicPrediction = AlgoBasicPrediction()

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
				if "none" in stock["predictions"]["basic"][index]["action"]:
					stock["predictions"]["basic"][index]["action"] = "sell"
				else:
					if "sell" not in stock["predictions"]["basic"][index]["action"]:
						print("({classname})# [CalculateBasicPrediction] ({0}) Prediction changed to SELL {1}".format(stock["ticker"],stock["price"],classname=self.ClassName))
						# Call for update callback
						#if self.StockSimplePredictionChangeCallback is not None:
						#	self.StockSimplePredictionChangeCallback({
						#		"ticker"	: stock["ticker"],
						#		"price"		: stock["price"],
						#		"pred_prev"	: stock["predictions"]["basic"][index]["action"],
						#		"pred_curr"	: "sell"
						#	})
						stock["predictions"]["basic"][index]["action"] = "sell"
			elif x[low] > stock["price"]:
				if "none" in stock["predictions"]["basic"][index]["action"]:
					stock["predictions"]["basic"][index]["action"] = "buy"
				else:
					if "buy" not in stock["predictions"]["basic"][index]["action"]:
						print("({classname})# [CalculateBasicPrediction] ({0}) Prediction changed to BUY {1}".format(stock["ticker"],stock["price"],classname=self.ClassName))
						# Call for update callback
						#if self.StockSimplePredictionChangeCallback is not None:
						#	self.StockSimplePredictionChangeCallback({
						#		"ticker"	: stock["ticker"],
						#		"price"		: stock["price"],
						#		"pred_prev"	: stock["predictions"]["basic"][index]["action"],
						#		"pred_curr"	: "buy"
						#	})
						stock["predictions"]["basic"][index]["action"] = "buy"
			else:
				if "none" in stock["predictions"]["basic"][index]["action"]:
					stock["predictions"]["basic"][index]["action"] = "hold"
				else:
					if "hold" not in stock["predictions"]["basic"][index]["action"]:
						print("({classname})# [CalculateBasicPrediction] ({0}) Prediction changed to HOLD {1}".format(stock["ticker"],stock["price"],classname=self.ClassName))
						# Call for update callback
						#if self.StockSimplePredictionChangeCallback is not None:
						#	self.StockSimplePredictionChangeCallback({
						#		"ticker"	: stock["ticker"],
						#		"price"		: stock["price"],
						#		"pred_prev"	: stock["predictions"]["basic"][index]["action"],
						#		"pred_curr"	: "hold"
						#	})
						stock["predictions"]["basic"][index]["action"] = "hold"
		except Exception as e:
			print("({classname})# [EXCEPTION] (CalculateBasicPrediction) {0} {1}".format(stock["ticker"],str(e),classname=self.ClassName))
		
		return stock

class StockMarketApi():
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
		error = False
		try:
			objtk = yf.Ticker(ticker)
			time.sleep(self.Delay)
			df_stock = objtk.history(period="1d", interval="5m")
			time.sleep(self.Delay)
			price = "{0:.3f}".format(df_stock["Close"].iloc[-1])
		except Exception as e:
			print("({classname})# [EXCEPTION] (GetStockCurrentPrice) {0} {1}".format(ticker,str(e),classname=self.ClassName))
			price = "0"
			error = True
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
		except Exception as e:
			print("({classname})# [EXCEPTION] GetStockHistory {0} {1} {2}".format(ticker,period,interval,classname=self.ClassName))
			return True, []
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
		self.API 						= StockMarketApi()

		# Callbacks
		self.FullLoopPerformedCallback 				= None
		self.StockChangeCallback 					= None
		self.ThresholdEventCallback 				= None
		self.FirstRunDoneCallback 					= None
		self.StockMarketOpenCallback 				= None
		self.StockMarketCloseCallback				= None
		self.StockSimplePredictionChangeCallback 	= None
		self.StockChangeLocker 						= threading.Lock()

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
	
	def WaitForMinionsToFinish(self):
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

	def StockMinion(self, index):
		self.LogMSG("({classname})# [MINION] Reporting for duty ({0})".format(index,classname=self.ClassName), 5)
		# Update jobless minons
		self.ThreadPoolLocker.acquire()
		self.JoblessMinions += 1
		self.ThreadPoolLocker.release()
		Interval = 0.25

		algos = StockCalculation()
		algos.StockSimplePredictionChangeCallback = self.StockSimplePredictionChangeCallback
		atock_api = StockMarketApi()

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
					error, stock["price"] = self.API.GetStockCurrentPrice(ticker) # Get stock price
					if error is True:
						stock["price"] = None
					else:
						error, stock["1D"] = atock_api.Get1D(ticker)	# Get 1 day history
						if error is True:
							stock["1D"] = None
						else:
							algos.CalculateBasicPrediction(stock, "1D")
						error, stock["5D"] = atock_api.Get5D(ticker)	# Get 5 days history
						if error is True:
							stock["5D"] = None
						else:
							algos.CalculateBasicPrediction(stock, "5D")
						error, stock["1MO"] = atock_api.Get1MO(ticker)	# Get 1 month history
						if error is True:
							stock["1MO"] = None
						else:
							algos.CalculateBasicPrediction(stock, "1MO")
						error, stock["3MO"] = atock_api.Get3MO(ticker)	# Get 3 months history
						if error is True:
							stock["3MO"] = None
						else:
							algos.CalculateBasicPrediction(stock, "3MO")
						error, stock["6MO"] = atock_api.Get6MO(ticker)	# Get 6 months history
						if error is True:
							stock["6MO"] = None
						else:
							algos.CalculateBasicPrediction(stock, "6MO")
						
						if stock["1D"] is not None and stock["5D"] is not None:
							today_open = stock["1D"][0]
							for idx, item in enumerate(stock["5D"]):
								if item["date"] == today_open["date"]:
									stock["prev_market_price"] = stock["5D"][idx-1]["close"]

						stock["1D_statistics"]  	= self.CalculateBasicStatistics(stock["1D"])
						stock["5D_statistics"]  	= self.CalculateBasicStatistics(stock["5D"])
						stock["1MO_statistics"] 	= self.CalculateBasicStatistics(stock["1MO"])

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
						
						#if self.StockChangeCallback is not None:
						#	self.StockChangeLocker.acquire()
						#	self.StockChangeCallback(stock)
						#	self.StockChangeLocker.release()
						
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
				if self.StockChangeLocker.locked is True:
					self.StockChangeLocker.release()
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
			"updated"			: False,
			"pulled"			: False,
			"ts_last_updated"	: 0,
			"1D_statistics"		: {},
			"5D_statistics"		: {},
			"1MO_statistics"	: {},
			"thresholds"		: [],
			"predictions"		: {
				"basic": [
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					}
				]
			}
		}
	
	def AppendStock(self, stock):
		self.Locker.acquire()
		try:
			stock["ts_last_updated"] 		= 0
			stock["1D_statistics"] 			= {}
			stock["5D_statistics"] 			= {}
			stock["1MO_statistics"] 		= {}
			stock["thresholds"] 			= []
			stock["predictions"]			= {
				"basic": [
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					},
					{
						"action"		: "none"
					}
				]
			}
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