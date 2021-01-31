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

import yfinance as yf
import pandas as pd
import math
import sqlite3

from mksdk import MkSFile
from mksdk import MkSSlaveNode
from mksdk import MkSScheduling

class StockMarket():
	def __init__(self):
		self.ClassName					= "StockMarket"
		self.CacheDB 					= {}
		self.WorkerRunning 				= False
		self.Locker						= threading.Lock()
		self.FirstStockUpdateRun 		= False
		self.MarketOpen 				= False
		self.MarketPollingInterval 		= 1

		self.FullLoopPerformedCallback 	= None
	
	def Start(self):
		self.WorkerRunning = True
		print("({classname})# Start".format(classname=self.ClassName))
		_thread.start_new_thread(self.StockMonitorWorker, ())

	def Stop(self):
		self.WorkerRunning = False
		print("({classname})# Stop".format(classname=self.ClassName))
	
	def StockMonitorWorker(self):
		while self.WorkerRunning is True:
			try:
				access_stocks_database = False
				currTime = datetime.datetime.now().time()
				if (currTime > datetime.time(16,25) and currTime < datetime.time(23,5)):
					self.MarketOpen = True
				else:
					self.MarketOpen = False
				if self.MarketOpen is True or self.FirstStockUpdateRun is False:
					for ticker in self.CacheDB:
						self.Locker.acquire()
						stock = self.CacheDB[ticker]
						if stock["pulled"] is False:
							print("({classname})# Update stock ({0})".format(ticker,classname=self.ClassName))
							access_stocks_database = True
							# Update stock info
							stock["price"] 	 = self.GetStockCurrentPrice(ticker)
							stock["1MO"] 	 = self.Get1MO(ticker)
							stock["5D"] 	 = self.Get5D(ticker)
							stock["pulled"]  = True
							stock["updated"] = True
							self.Locker.release()
							break
						self.Locker.release()
					if access_stocks_database is False:
						print("({classname})# Clean PULLED flag".format(classname=self.ClassName))
						self.FirstStockUpdateRun = True
						if self.FullLoopPerformedCallback is not None:
							self.FullLoopPerformedCallback()
						self.Locker.acquire()
						for ticker in self.CacheDB:
							stock = self.CacheDB[ticker]
							stock["pulled"] = False
						self.Locker.release()
				time.sleep(self.MarketPollingInterval)
			except Exception as e:
				print("({classname})# [Exeption] ({0})".format(e,classname=self.ClassName))

	def AppendStock(self, stock):
		self.Locker.acquire()
		try:
			self.CacheDB[stock["ticker"]] = stock
		except:
			pass
		self.Locker.release()
	
	def GetStockInformation(self, ticker):
		print("({classname})# [GetStockInformation] ({0})".format(ticker,classname=self.ClassName))
		self.Locker.acquire()
		try:
			if ticker in self.CacheDB:
				stock = self.CacheDB[ticker]
				if stock["updated"] is False:
					stock["price"]   = self.GetStockCurrentPrice(ticker)
					stock["1MO"] 	 = self.Get1MO(ticker)
					stock["5D"] 	 = self.Get5D(ticker)
					stock["updated"] = True
					stock["pulled"]  = True
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
	
	def Get5D(self, ticker):
		'''
			Open,High,Low,Close,Volume,Dividends,Stock Splits
		'''
		hist = []
		objtk = yf.Ticker(ticker)
		data = objtk.history(period="5d", interval="5m")
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

class StockDB():
	def __init__(self, path):
		path = os.path.join("", path)
		self.ClassName	= "StockDB"
		self.DB 		= sqlite3.connect(path, check_same_thread=False)
		self.CURS		= self.DB.cursor()

		self.BuildSchema()
	
	def BuildSchema(self):
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_history" (
							"timestamp"	REAL NOT NULL,
							"date"	TEXT NOT NULL,
							"ticker"	TEXT NOT NULL,
							"price"	REAL NOT NULL,
							"action"	TEXT NOT NULL
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_info" (
							"name"	TEXT,
							"ticker"	TEXT,
							"sector"	TEXT,
							"industry"	TEXT,
							"market_price"	REAL
						);''')
				
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "portfolios" (
							"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
							"name"	TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stock_to_portfolio" (
							"ticker"	TEXT NOT NULL,
							"potrfolio_id"	INTEGER NOT NULL
						);''')

	def GetPortfolios(self):
		query = "SELECT * FROM portfolios"
		self.CURS.execute(query)
		
		portfolios = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				portfolios.append({
					"id": row[0],
					"name": row[1]
				})
		return portfolios
	
	def GetStocks(self):
		query = "SELECT * FROM stocks_info"
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"name": row[0],
					"ticker": row[1],
					"sector": row[2],
					"industry": row[3],
					"market_price": row[4]
				})
		return stocks

	def GetPortfolioStocks(self, id):
		stocks = []
		if 0 == id:
			query = '''
			SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, stock_to_portfolio.potrfolio_id, hist_max, hist_min FROM stocks_info 
			INNER JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			INNER JOIN (
				SELECT ticker, ABS(SUM(price * action * amount)) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
				FROM stocks_history 
				GROUP BY ticker) as hist ON hist.ticker == stocks_info.ticker
			INNER JOIN (
				SELECT ticker, MAX(price) as hist_max, MIN(price) as hist_min
				FROM stocks_history
				WHERE action == -1
				GROUP BY ticker) as tbl_actions ON tbl_actions.ticker == stocks_info.ticker
			'''
		else:
			query = '''
			SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, stock_to_portfolio.potrfolio_id, hist_max, hist_min FROM stocks_info 
			INNER JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			INNER JOIN (
				SELECT ticker, ABS(SUM(price * action * amount)) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
				FROM stocks_history 
				GROUP BY ticker) as hist ON hist.ticker == stocks_info.ticker
			INNER JOIN (
				SELECT ticker, MAX(price) as hist_max, MIN(price) as hist_min
				FROM stocks_history
				WHERE action == -1
				GROUP BY ticker) as tbl_actions ON tbl_actions.ticker == stocks_info.ticker
			WHERE stock_to_portfolio.potrfolio_id == {0}
			'''.format(id)
		self.CURS.execute(query)
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"ticker": row[0],
					"name": row[1],
					"market_price": row[2],
					"curr_price_sum": row[3],
					"hist_price_sum": row[4],
					"amount_sum": row[5],
					"potrfolio_id": row[6],
					"hist_max": row[7],
					"hist_min": row[8]
				})
		return stocks
	
	def GetStockHistory(self, ticker):
		query = '''
			SELECT timestamp, date, price, amount, name, action FROM stocks_history
			INNER JOIN actions ON actions.id == stocks_history.action
			WHERE stocks_history.ticker == "{0}"
		'''.format(ticker)
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"timestamp": row[0],
					"date": row[1],
					"price": row[2],
					"amount": row[3],
					"action": row[5],
					"action_name": row[4]
				})
		return stocks

class Context():
	def __init__(self, node):
		self.ClassName					= "Apllication"
		self.Timer						= MkSScheduling.TimeSchedulerThreadless()
		self.Node						= node
		self.File						= MkSFile.File()
		self.Market 					= StockMarket()
		self.SQL 						= StockDB("stocks.db")
		# States
		self.States = {
		}
		# Handlers
		self.Node.ApplicationRequestHandlers	= {
			'get_sensor_info':			self.GetSensorInfoHandler,
			'get_portfolios':			self.GetPortfoliosHandler,
			'get_portfolio_stocks':		self.GetPortfolioStocksHandler,
			'get_stock_history':		self.GetStockHistoryHandler,
			'undefined':				self.UndefindHandler
		}
		self.Node.ApplicationResponseHandlers	= {
			'undefined':				self.UndefindHandler
		}
		self.Node.Operations[0x5000]	= {
			0x0:	self.OperationPing,
			0x1:	self.OperationInfo
		}
		# Application variables

		self.Timer.AddTimeItem(10, self.PrintConnections)
		self.Market.FullLoopPerformedCallback = self.FullLoopPerformedEvent
	
	def FullLoopPerformedEvent(self):
		pass

	def GetStockHistoryHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetStockHistoryHandler]".format(classname=self.ClassName),5)
		
		return {
			"history": self.SQL.GetStockHistory(payload["ticker"])
		}
	
	def GetPortfoliosHandler(self, sock, packet):
		self.Node.LogMSG("({classname})# [GetPortfoliosHandler]".format(classname=self.ClassName),5)
		
		return {
			"portfolios": self.SQL.GetPortfolios()
		}
	
	def GetPortfolioStocksHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler]".format(classname=self.ClassName),5)
		
		potrfolio_id = payload["portfolio_id"]
		db_stocks = self.SQL.GetPortfolioStocks(potrfolio_id)
		
		stocks = []
		portfolio_earnings = 0.0
		portfolio_investment = 0.0
		if len(db_stocks) > 0:
			for db_stock in db_stocks:
				ticker = db_stock["ticker"]
				stock = self.Market.GetStockInformation(ticker)

				if stock is not None:
					#price = self.Market.GetStockCurrentPrice(ticker)
					price = stock["price"]
					earnings = float("{0:.3f}".format(price * db_stock["amount_sum"] - db_stock["hist_price_sum"]))
					portfolio_earnings += earnings
					portfolio_investment += price * db_stock["amount_sum"]

					#data = self.Market.Get5D(ticker) # 5 Day history price
					data = stock["5D"]
					w_min, w_max = self.Market.CalculateMinMax(data)
					w_slope, w_b, w_r2 = self.Market.GetRegressionLineStatistics(data)
					w_var, w_std = self.Market.GetBasicStatistics(data)

					#data = self.Market.Get1MO(ticker) # One month history price
					data = stock["1MO"]
					m_min, m_max = self.Market.CalculateMinMax(data)
					m_slope, m_b, m_r2 = self.Market.GetRegressionLineStatistics(data)
					m_var, m_std = self.Market.GetBasicStatistics(data)
					stocks.append({
						"ticker":ticker,
						"name": db_stock["name"],
						"number": db_stock["amount_sum"],
						"earnings": earnings,
						"market_price": price,
						"hist_price_min": db_stock["hist_min"],
						"hist_price_max": db_stock["hist_max"],
						"statistics": {
							"weekly": {
								"min": float("{0:.2f}".format(w_min)),
								"max": float("{0:.2f}".format(w_max)),
								"slope": float("{0:.2f}".format(w_slope)),
								"std": float("{0:.2f}".format(w_std)),
								"slope_offset": float("{0:.2f}".format(w_b)),
								"r_value": float("{0:.2f}".format(w_r2)),
								"varience": float("{0:.2f}".format(w_var))
							},
							"monthly": {
								"min": float("{0:.2f}".format(m_min)),
								"max": float("{0:.2f}".format(m_max)),
								"slope": float("{0:.2f}".format(m_slope)),
								"std": float("{0:.2f}".format(m_std)),
								"slope_offset": float("{0:.2f}".format(m_b)),
								"r_value": float("{0:.2f}".format(m_r2)),
								"varience": float("{0:.2f}".format(m_var))
							}
						}
					})
		portfolio_earnings = float("{0:.3f}".format(portfolio_earnings))
		return {
			"portfolio": {
				"name": payload["portfolio_name"],
				"earnings": portfolio_earnings,
				"investment": portfolio_investment,
				"stocks_count": len(db_stocks)
			},
			"stocks": stocks
		}
	
	def UndefindHandler(self, sock, packet):
		print ("UndefindHandler")
	
	def GetSensorInfoHandler(self, sock, packet):
		print ("({classname})# GetSensorInfoHandler ...".format(classname=self.ClassName))

		return {
		}
	
	def OperationPing(self, sock, packet):
		source		= self.Node.BasicProtocol.GetSourceFromJson(packet)
		payload		= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		index		= payload["index"]
		subindex	= payload["subindex"]
		direction	= payload["direction"]
		self.Node.LogMSG("({classname})# [OperationPing] {0}".format(source,classname=self.ClassName),5)

		return {
			'return_code': 'ok'
		}
	
	def OperationInfo(self, sock, packet):
		source		= self.Node.BasicProtocol.GetSourceFromJson(packet)
		payload		= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [OperationInfo] {0}".format(source,classname=self.ClassName),5)
		return {
		}

	def OnGetNodeInfoHandler(self, info):
		self.Node.LogMSG("({classname})# [OnGetNodeInfoHandler] [{0}, {1}, {2}]".format(info["uuid"],info["name"],info["type"],classname=self.ClassName),5)

	def NodeSystemLoadedHandler(self):
		self.Node.LogMSG("({classname})# Loading system ...".format(classname=self.ClassName),5)
		stocks = self.SQL.GetStocks()
		if stocks is not None:
			if len(stocks) > 0:
				for stock in stocks:
					#self.Node.LogMSG("({classname})# {0}".format(stock,classname=self.ClassName),5)
					self.Market.AppendStock({
						"ticker": 	stock["ticker"],
						"price": 	0,
						"1MO": 		None,
						"5D": 		None,
						"updated": 	False,
						"pulled": 	False
					})
		self.Market.Start()
	
	def OnGetNodesListHandler(self, uuids):
		print ("OnGetNodesListHandler", uuids)

	def PrintConnections(self):
		self.Node.LogMSG("\nTables:",5)
		connections = THIS.Node.GetConnectedNodes()
		for idx, key in enumerate(connections):
			node = connections[key]
			self.Node.LogMSG("	{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(str(idx),node.Obj["local_type"],node.Obj["uuid"],node.IP,node.Obj["listener_port"],node.Obj["type"],node.Obj["pid"],node.Obj["name"]),5)
		self.Node.LogMSG("",5)
	
	def OnNodeWorkTick(self):
		self.Timer.Tick()

Node = MkSSlaveNode.SlaveNode()
THIS = Context(Node)

def signal_handler(signal, frame):
	THIS.Market.Stop()
	THIS.Node.Stop("Accepted signal from other app")

def main():
	signal.signal(signal.SIGINT, signal_handler)
	THIS.Node.SetLocalServerStatus(True)
	
	# Node callbacks
	THIS.Node.NodeSystemLoadedCallback				= THIS.NodeSystemLoadedHandler
	THIS.Node.OnGetNodesListCallback				= THIS.OnGetNodesListHandler
	THIS.Node.OnGetNodeInfoCallback					= THIS.OnGetNodeInfoHandler
	
	THIS.Node.Run(THIS.OnNodeWorkTick)
	THIS.Node.LogMSG("({classname})# Exit node.".format(classname=THIS.Node.ClassName),5)

if __name__ == "__main__":
	main()
