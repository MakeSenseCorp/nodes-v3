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
from datetime import datetime

import yfinance as yf
import pandas as pd
import math
import sqlite3

from mksdk import MkSFile
from mksdk import MkSSlaveNode
from mksdk import MkSScheduling
from mksdk import MkSFileUploader

from classes import StockMarketAPI
from classes import StockMarketRemote
from classes import StockMarket
from classes import StockDataBase
from classes import NasdaqApi
from classes import AlgoMath
from classes import Algos

class Context():
	def __init__(self, node):
		self.ClassName					= "Apllication"
		self.Timer						= MkSScheduling.TimeSchedulerThreadless()
		self.Node						= node
		self.File						= MkSFile.File()
		self.MarketRemote 				= StockMarketRemote.StockMarket()
		self.Market 					= StockMarket.StockMarket(node, self.MarketRemote)
		self.Math 						= AlgoMath.AlgoMath()
		self.Nasdaq						= NasdaqApi.Nasdaq(node)
		self.BasicPrediction 			= Algos.BasicPrediction()
		self.StockCalulator 			= StockMarketRemote.StockCalculation()
		self.SQL 						= StockDataBase.StockDB("stocks.db")
		# States
		self.States = {
		}
		# Handlers
		self.Node.ApplicationRequestHandlers	= {
			'get_sensor_info':					self.GetSensorInfoHandler,
			'get_portfolios':					self.GetPortfoliosHandler,
			'get_portfolio_stocks':				self.GetPortfolioStocksHandler,
			'get_stock_history':				self.GetStockHistoryHandler,
			'append_new_action':				self.AppendNewActionHandler,
			'create_new_portfolio':				self.CreateNewPortfolioHandler,
			'import_stocks':					self.ImportStocksHandler,
			'export_stocks': 					self.ExportStocksHandler,
			'upload_file':						self.Request_UploadFileHandler,
			'load_csv':							self.LoadCSVHandler,
			'download_stock_history':			self.DownloadStockHistoryHandler,
			'download_stock_info':				self.DownloadStockInfoHandler,
			'get_db_stocks':					self.GetDBStocksHandler,
			'get_stock_portfolios':				self.GetStockPortfolios,
			'set_stock_portfolios':				self.SetStockPortfolios,
			'delete_portfolio':					self.DeletePortfolioHandler,
			'db_insert_stock':					self.DBInsertStockHandler,
			'db_delete_stock':					self.DBDeleteStockHandler,
			'db_delete_action':					self.DBDeleteActionHandler,
			'calulate_basic_prediction':		self.CalculateBasicPredictionHandler,
			'threshold':						self.ThresholdHandler,
			'portfolio_history_change':			self.PortfolioHistoryChangeHandler,
			'undefined':						self.UndefindHandler
		}
		self.Node.ApplicationResponseHandlers	= {
			'undefined':				self.UndefindHandler
		}
		self.Node.Operations[0x5000]	= {
			0x0:	self.OperationPing,
			0x1:	self.OperationInfo
		}
		# Application variables
		self.UploadLocker 				= threading.Lock()
		self.LocalStoragePath 			= "import"

		self.MarketRemote.FullLoopPerformedCallback 				= self.FullLoopPerformedEvent
		# self.MarketRemote.StockChangeCallback 					= self.StockChangeEvent
		self.MarketRemote.FirstRunDoneCallback						= self.FirstRunDoneEvent
		self.MarketRemote.StockMarketOpenCallback					= self.StockMarketOpenEvent
		self.MarketRemote.StockMarketCloseCallback					= self.StockMarketCloseEvent
		self.MarketRemote.StockSimplePredictionChangeCallback 		= self.StockSimplePredictionChangeEvent
		self.MarketRemote.ThresholdEventCallback 					= self.ThresholdEvent
		self.CurrentPortfolio 			= 0

		self.Nasdaq.BindHandler()
		self.Market.BindHandler()

		# self.Timer.AddTimeItem(10, self.PrintConnections) # In scope of main Node thread
	
	def ThresholdEvent(self, ticker, price, threshold):
		self.Node.LogMSG("({classname})# [ThresholdEvent]".format(classname=self.ClassName),5)

		if "risk" in threshold["name"]:
			html = '''
				<table>
					<tr>
						<td><span>Ticker</span></td>
						<td><span>{0}</span></td>
					</tr>
					<tr>
						<td><span>Price</span></td>
						<td><span>{1}</span></td>
					</tr>
					<tr>
						<td><span>Limit</span></td>
						<td><span>{2}</span></td>
					</tr>
				</table>
			'''.format(ticker, price, threshold["value"])
		else:
			html = '''
				<table>
					<tr>
						<td><span>Ticker</span></td>
						<td><span>{0}</span></td>
					</tr>
					<tr>
						<td><span>Price</span></td>
						<td><span>{1}</span></td>
					</tr>
				</table>
			'''
		# self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Risk", html)

	'''
		index: Prediction type (1D = 0, 5D = 1, 1MO = 2, 3MO = 3, 6MO = 4, 1Y = 5)
	'''
	def StockSimplePredictionChangeEvent(self, ticker, index):
		self.Node.LogMSG("({classname})# [StockSimplePredictionChangeEvent]".format(classname=self.ClassName),5)

		# We need to send mail only on prediction of 5D and 1MO
		if index not in [1,2]:
			return
		
		stock = self.MarketRemote.CacheDB[ticker]
		if stock is not None:
			try:
				prediction 			= stock["predictions"]["basic"][index]
				current_action  	= prediction["action"]["current"]

				self.Node.LogMSG("({classname})# [StockSimplePredictionChangeEvent] Send Mail ({0} {1} {2})".format(ticker, stock["price"], current_action, classname=self.ClassName),5)
				html = '''
					<table>
						<tr>
							<td><span>Ticker</span></td>
							<td><span>{0}</span></td>
						</tr>
						<tr>
							<td><span>Price</span></td>
							<td><span>{1}</span></td>
						</tr>
						<tr>
							<td><span>Prediction</span></td>
							<td><span>{2}</span></td>
						</tr>
					</table>
				'''.format(ticker, stock["price"], current_action)
				# self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Prediction Change", html)
			except Exception as e:
				self.Node.LogMSG("({classname})# [EXCEPTION] (StockSimplePredictionChangeEvent) {0} {1}".format(ticker,str(e),classname=self.ClassName),5)

	def StockMarketCloseEvent(self):
		pass

	def StockMarketOpenEvent(self):
		pass

	def FirstRunDoneEvent(self):
		self.Node.LogMSG("({classname})# [FirstRunDoneEvent]".format(classname=self.ClassName),5)
		try:
			stocks = self.MarketRemote.GetCacheDB()
			html_rows = ""
			for ticker in stocks:
				stock = stocks[ticker]

				basic_pred_html = ""
				for item in stock["predictions"]["basic"]:
					if "buy" in item["action"]["current"]:
						color = "GREEN"
					elif "sell" in item["action"]["current"]:
						color = "RED"
					else:
						color = "BLACK"
					basic_pred_html += '''<td><span style="color:{0}">{1}</span></td>'''.format(color,item["action"]["current"])

				html_rows += '''
					<tr>
						<td><a href="#">{0}</a></td>
						<td>{1}</td>
						{2}
					</tr>
				'''.format(stock["ticker"], stock["price"],basic_pred_html)

			html = "<table>{0}</table>".format(html_rows)
			# self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Node Started", html)
		except:
			pass

	def FullLoopPerformedEvent(self):
		pass
	
	def AddRiskThresholdToStock(self, ticker):
		try:
			hist = self.SQL.GetBuyStocksWithLeftovers(ticker)
			if hist is not None:
				for item in hist:
					self.AddRiskThreshold(ticker, item["id"], item["price"], item["risk"])
				return True
		except Exception as e:
			print(e)
		return False
	
	'''
		Each stock can have one lower limit.
		When ever this limit reached user will have the message.
	'''
	def AddLowerLimitThreshold(self, ticker, value):
		try:
			# Check if limit already exist
			self.MarketRemote.AppendThreshold(ticker, {
				"stock_action_id": 0,
				"value": float(value),
				"type": 3,
				"activated": False,
				"name": "lower_limit_{0}".format(ticker)
			})
		except Exception as e:
			self.Node.LogMSG("({classname})# [EXCEPTION] AddLowerLimitThreshold {0}".format(str(e),classname=self.ClassName), 5)

	'''
		Each stock can have one upper limit.
		When ever this limit reached user will have the message.
	'''
	def AddUpperLimitThreshold(self, ticker, value):
		try:
			self.MarketRemote.AppendThreshold(ticker, {
				"stock_action_id": 0,
				"value": float(value),
				"type": 1,
				"activated": False,
				"name": "upper_limit_{0}".format(ticker)
			})
		except Exception as e:
			self.Node.LogMSG("({classname})# [EXCEPTION] AddUpperLimitThreshold {0}".format(str(e),classname=self.ClassName), 5)

	def AddRiskThreshold(self, ticker, act_id, price, risk):
		try:
			'''
				1 - Below
				2 - Equal
				3 - Above
			'''
			self.MarketRemote.AppendThreshold(ticker, {
				"stock_action_id": act_id,
				"value": float(price) * ((100.0 - float(risk)) / 100.0),
				"type": 1,
				"activated": False,
				"name": "risk"
			})
		except Exception as e:
			print(e)

	def PotfolioHistoryChangeWorker(self, portfolio_id):
		stock_api = StockMarketAPI.API()
		stocks_diff_list = []
		# Get portfolio's stocks
		stocks = self.SQL.GetStocksByPortfolioId(portfolio_id)
		for stock in stocks:
			ticker = stock["ticker"]
			self.Node.LogMSG("({classname})# [PotfolioHistoryChangeWorker] {0}".format(ticker, classname=self.ClassName),5)
			price_list = []
			sum_diff = 0.0
			# Get stock history 30 days
			error, history = stock_api.GetStockHistory(ticker, "1mo", "1d")
			for idx, item in enumerate(history):
				if idx == 0:
					continue
				price_curr = item["close"]
				price_prev = history[idx-1]["close"]
				price_diff = float(price_curr) - float(price_prev)
				price_list.append({
					"date": item["date"],
					"price_diff": price_diff,
					"price": price_curr
				})
				sum_diff += price_diff
			stocks_diff_list.append({
				"ticker": ticker,
				"data": price_list,
				"sum_diff": sum_diff,
				"total_diff": 0.0
			})
		
		#sum_diff = 0.0
		#stocks_diff_sum_list = {}
		#for item in stocks_diff_list:
		#	data = item["data"]
		#	for sample in data:
		#		if sample["date"] not in stocks_diff_sum_list:
		#			stocks_diff_sum_list[sample["date"]] = float(sample["price_diff"])
		#		else:
		#			stocks_diff_sum_list[sample["date"]] += float(sample["price_diff"])
		#		sum_diff += float(sample["price_diff"])
		#self.Node.LogMSG("({classname})# [PotfolioHistoryChangeWorker] {0}".format(sum_diff, classname=self.ClassName),5)

		buy_count = 0
		sum_diff = 0.0
		for item in stocks_diff_list:
			data = item["data"]
			stock_sum_diff = 0.0
			for sample in data:
				diff = float(sample["price_diff"])
				if diff > 0:
					if buy_count > 0:
						sum_diff += (diff * buy_count)
						stock_sum_diff += (diff * buy_count)
						buy_count = 0
				else:
					buy_count += 1
					sum_diff += diff
					stock_sum_diff += diff
			item["total_diff"] = stock_sum_diff
		
		self.Node.LogMSG("({classname})# [PotfolioHistoryChangeWorker] {0}".format(sum_diff, classname=self.ClassName),5)
	
		THIS.Node.EmitOnNodeChange({
			'event': "portfolio_history_change",
			'data': {
				"stocks": stocks_diff_list,
				"total_diff": sum_diff	
			}
		})

	def PortfolioHistoryChangeHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [PortfolioHistoryChangeHandler] {0}".format(payload,classname=self.ClassName),5)

		if "portfolio_id" in payload:
			portfolio_id = payload["portfolio_id"]
			_thread.start_new_thread(self.PotfolioHistoryChangeWorker, (portfolio_id,))

			return {
				"status": True
			}
		
		return {
			"status": False
		}

	def ThresholdHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [ThresholdHandler] {0}".format(payload,classname=self.ClassName),5)
		if "action" in payload:
			action = payload["action"]
			ticker = payload["ticker"]

			if "select" in action:
				threshold = self.SQL.GetStockThresholds(ticker)
				return {
					"thresholds": threshold
				}
			elif "insert" in action:
				pass
			elif "update" in action:
				upper = payload["upper"]
				lower = payload["lower"]
				runtime_thresholds = self.MarketRemote.GetRunTimeThresholds(ticker)

				# Update runtime engine
				if upper["enabled"] == True:
					self.AddUpperLimitThreshold(ticker, upper["value"]) # UPPER
				else:
					# Remove threshold
					for item in runtime_thresholds:
						if "upper_limit" in item["name"]:
							self.MarketRemote.RemoveThreshold(ticker, item["id"])
							break
				
				if lower["enabled"] == True:
					self.AddLowerLimitThreshold(ticker, lower["value"]) # LOWER
				else:
					# Remove threshold
					for item in runtime_thresholds:
						if "lower_limit" in item["name"]:
							self.MarketRemote.RemoveThreshold(ticker, item["id"])
							break
				
				# Update DB
				if self.SQL.GetStockThresholds(ticker) is None:
					pass
				else:
					# Update existing
					self.SQL.UpdateStockThreshold(upper["id"], upper["value"], upper["enabled"])
					self.SQL.UpdateStockThreshold(lower["id"], lower["value"], lower["enabled"])
			elif "delete" in action:
				pass
		
		return {
			"status": True
		}

	def CalculateBasicPredictionHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [CalculateBasicPredictionHandler] {0}".format(payload,classname=self.ClassName),5)
		try:
			ticker = payload["ticker"]
			stock = self.MarketRemote.GenerateEmtpyStock()
			stock["ticker"] = ticker
			error, stock["price"]	= self.MarketRemote.API.GetStockCurrentPrice(ticker)
			error, stock["1D"]		= self.MarketRemote.API.Get1D(ticker)
			error, stock["5D"]		= self.MarketRemote.API.Get5D(ticker)
			error, stock["1MO"]		= self.MarketRemote.API.Get1MO(ticker)
			error, stock["3MO"]		= self.MarketRemote.API.Get3MO(ticker)
			error, stock["6MO"]		= self.MarketRemote.API.Get6MO(ticker)

			calc = StockMarketRemote.StockCalculation()
			calc.CalculateBasicPrediction(stock, "1D")
			calc.CalculateBasicPrediction(stock, "5D")
			calc.CalculateBasicPrediction(stock, "1MO")
			calc.CalculateBasicPrediction(stock, "3MO")
			calc.CalculateBasicPrediction(stock, "6MO")
		except Exception as e:
			self.Node.LogMSG("({classname})# [EXCEPTION] CalculateBasicPredictionHandler {0} {1}".format(payload,str(e),classname=self.ClassName), 5)

		return {
			"stock": stock
		}

	# [CURRENTLY NOT IN USE]
	def StockChangeEvent(self, stock):
		self.Node.LogMSG("({classname})# [StockChangeEvent]".format(classname=self.ClassName),5)
		'''
		price 					= stock["price"]
		earnings 				= 0.0
		earnings 				= 0.0
		ticker 					= stock["ticker"]
		
		try:
			db_stock = self.SQL.GetStockExtetendedInfo(ticker)
			# Calculate actions min, max and summary
			if price > 0:
				if db_stock["amount_sum"] is not None and db_stock["hist_price_sum"] is not None:
					earnings = float("{0:.3f}".format(db_stock["hist_price_sum"]))
					if (price * db_stock["amount_sum"]) > 0:
						earnings = float("{0:.3f}".format(price * db_stock["amount_sum"] - db_stock["hist_price_sum"]))
				else:
					db_stock["amount_sum"] 	= 0.0
					db_stock["hist_min"] 	= 0.0
					db_stock["hist_max"]	= 0.0
			
			THIS.Node.EmitOnNodeChange({
				'event': "stock_info",
				'data': [
					{
						"ticker":ticker,
						"name": db_stock["name"],
						"number": db_stock["amount_sum"],
						"earnings": earnings,
						"market_price": price,
						"hist_price_min": db_stock["hist_min"],
						"hist_price_max": db_stock["hist_max"],
						"statistics": {
						}
					} 	
				]
			})
		except Exception as e:
			self.Node.LogMSG("({classname})# [StockChangeEvent] ERROR {0} {1}".format(ticker,e,classname=self.ClassName),5)
		'''

	def DBDeleteStockHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DBDeleteStockHandler] {0}".format(payload,classname=self.ClassName),5)
		ticker = payload["ticker"]

		self.SQL.DeleteStock(ticker)
		self.MarketRemote.RemoveStock(ticker)
		# Delete all thresholds
		self.SQL.DeleteallThresholds(ticker)

		return {
			"status": True
		}
	
	def DBDeleteActionHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DBDeleteActionHandler] {0}".format(payload,classname=self.ClassName),5)

		# Get item to be deleted
		del_act_id 	= payload["id"]
		ticker 		= payload["ticker"]
		del_act = self.SQL.GetStockHistoryActionById(del_act_id)
		if del_act["action"] == -1:
			# del_act is a BUY action
			# Delete all rows from stocks_history_sell_info table by stocks_history_buy_id
			self.SQL.GetStockHistorySellInfoByBuyId(del_act_id)
		else:
			# del_act is a SELL action
			# Get all rows for this id
			hist_sell_info = self.SQL.GetStockHistorySellInfoBySellId(del_act_id)
			for item in hist_sell_info:
				# Update buy leftovers
				self.SQL.UpdateStockActionLeftoverById(item["stocks_history_buy_id"], item["quantity"])
				# Delete all rows from stocks_history_sell_info table by stocks_history_sell_id
				self.SQL.DeleteStockHistorySellInfoBySellId(del_act_id)
			pass

		# Delete action
		self.SQL.DeleteActionById(del_act_id)
		# Remove risk monitor for this action
		self.MarketRemote.RemoveThresholdByStockActionId(ticker, del_act_id)

		return {
			"status": True
		}

	def CheckForDict(self, obj, name):
		if type(obj) == dict:
			value = obj["raw"]
		else:
			value = obj
		
		return value
		
	def DBInsertStockHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DBInsertStockHandler] {0}".format(payload,classname=self.ClassName),5)

		ticker = payload["ticker"]

		# Check if stock already in the DB
		if self.SQL.StockExist(ticker) is False:
			info = self.MarketRemote.API.GetStockInfoRaw(ticker)
			self.Node.LogMSG("({classname})# [DBInsertStockHandler] {0} Append to stock DB".format(payload,classname=self.ClassName),5)
			sector = ""
			if "sector" in info:
				sector = info["sector"]
			industry = ""
			if "industry" in info:
				industry = info["industry"]
			self.SQL.InsertStock({
				'name': info["shortName"],
				'ticker': ticker,
				'market_price': self.CheckForDict(info["previousClose"], "previousClose"),
				'sector': info["sector"],
				'industry': info["industry"]
			})

			# Add UPPER & LOWER threshold
			if self.SQL.GetStockThresholds(ticker) is None:
				# Insert new row
				self.SQL.InsertStockThreshold({
					"ticker": ticker,
					"value": 0.0,
					"type": 10
				})
				self.SQL.InsertStockThreshold({
					"ticker": ticker,
					"value": 0.0,
					"type": 11
				})
			# Append thresholds to runtime
			self.AddUpperLimitThreshold(ticker, 0.0) # UPPER
			self.AddLowerLimitThreshold(ticker, 0.0) # LOWER
			
			self.Node.LogMSG("({classname})# [DBInsertStockHandler] {0} Append to stock monitoring".format(payload,classname=self.ClassName),5)
			# Append to stock monitoring
			self.MarketRemote.AppendStock(payload["ticker"].upper())
		return {
			"status": True
		}

	def DeletePortfolioHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DeletePortfolioHandler] {0}".format(payload,classname=self.ClassName),5)
		self.SQL.DeletePortfolio(payload["id"])
		return {
			"portfolios": self.SQL.GetPortfolios()
		}

	def SetStockPortfolios(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [SetStockPortfolios] {0}".format(payload,classname=self.ClassName),5)
		if payload["status"] is True:
			self.SQL.InsertStockPortfolio(payload)
		else:
			self.SQL.DeleteStockPortfolio(payload)
		return {
			"portfolios": self.SQL.GetStockPortfolios(payload["ticker"])
		}

	def GetStockPortfolios(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetStockPortfolios] {0}".format(payload,classname=self.ClassName),5)
		return {
			"portfolios": self.SQL.GetStockPortfolios(payload["ticker"])
		}

	def GetDBStocksHandler(self, sock, packet):
		db_stocks = self.SQL.GetPortfolioStocks(0)
		return {
			"stocks": db_stocks
		}

	def LoadCSVHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [LoadCSVHandler] {0}".format(payload["file_name"],classname=self.ClassName),5)
		csv = self.File.Load(os.path.join(".","import",payload["file_name"]))

		exist = 0
		data  = []
		if csv is not None and len(csv) > 0:
			tickers = self.SQL.GetTickers()
			rows = csv.split("\n")
			for row in rows:
				if row is not None:
					cols = row.split(',')
					if len(cols) > 3:
						if cols[1] in tickers:
							exist = 1
						else:
							exist = 0
						# TODO - Check each field for correctness
						data.append({
							"date": 	cols[0],
							"ticker": 	cols[1],
							"price":  	cols[2],
							"fee": 		cols[3],
							"amount": 	cols[4],
							"action": 	cols[5],
							"exists": 	exist
						})
			
			return {
				'status': 'success',
				'file_name': payload["file_name"],
				'stocks': data
			}

		return {
			'status': 'failed',
			'file_name': payload["file_name"],
			'stocks': data
		}

	def Request_UploadFileHandler(self, sock, packet):
		self.UploadLocker.acquire()
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [Request_UploadFileHandler] {0}".format(payload["upload"]["chunk"], classname=self.ClassName),5)

		if payload["upload"]["chunk"] == 1:
			self.Uploader.AddNewUploader(payload["upload"])
		else:
			self.Uploader.UpdateUploader(payload["upload"])
		
		self.UploadLocker.release()
		return {
			'status': 'accept',
			'chunk': payload["upload"]["chunk"],
			'file': payload["upload"]["file"]
		}

	def ExportStocksHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [ExportStocksHandler]".format(classname=self.ClassName),5)
		return {
			'status': 'success'
		}
	
	def GenerateTimestamp(self, month, day, year):
		if month < 1 or month > 12:
			return None
		if day < 1 or day > 31:
			return None
		if year < 1900:
			return None

		ts_date = date(int(year),int(month),int(day))
		return time.mktime(ts_date.timetuple())
	
	def ImportStocksHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [ImportStocksHandler]".format(classname=self.ClassName),5)
		self.MarketRemote.PauseMarket()
		
		portfolio_id = 1
		if payload["portfolio_checked"] is True:
			if False == self.SQL.PortfolioExist(payload["portfolio_name"]):
				self.Node.LogMSG("({classname})# [ImportStocksHandler] Create portfolio ({0})".format(payload["portfolio_name"], classname=self.ClassName),5)
				portfolio_id = self.SQL.InsertPortfolio(payload["portfolio_name"])
		stocks = payload["stocks"]

		THIS.Node.EmitOnNodeChange({
			'event': "upload_progress",
			'data': {
				"status": "inprogress",
				"precentage": "10%",
				"message": "Importing Stocks.",
				"file": ""
			}
		})

		for idx, item in enumerate(stocks):
			date 	= item["date"].replace("/","-")
			ticker 	= item["ticker"].upper()
			price 	= item["price"]
			amount 	= item["amount"]
			fee 	= item["fee"]
			action 	= item["action"]

			date_arr = date.split("-")
			timestamp = self.GenerateTimestamp(int(date_arr[0]), int(date_arr[1]), int(date_arr[2]))
			if timestamp is not None:
				self.SQL.InsertStockHistory({
					'timestamp': timestamp,
					'date': "{0} 00:00:00".format(date),
					'ticker': ticker,
					'price': price,
					'action': action,
					'amount': amount,
					'fee': fee
				})

				if self.SQL.StockExist(ticker) is False:
					self.Node.LogMSG("({classname})# [ImportStocksHandler] Insert Stock {0}".format(ticker,classname=self.ClassName),5)
					info = None
					try:
						info = self.MarketRemote.API.GetStockInfoRaw(ticker)
					except Exception as e:
						self.Node.LogMSG("({classname})# [ImportStocksHandler] ERROR {0}".format(e,classname=self.ClassName),5)
					
					if info is None:
						self.SQL.InsertStock({
							'name': "",
							'ticker': ticker,
							'market_price': float(price),
							'sector':"",
							'industry': ""
						})
					else:
						name = ""
						if "shortName" in info:
							name = info["shortName"]
						sector = ""
						if "sector" in info:
							sector = info["sector"]
						industry = ""
						if "industry" in info:
							industry = info["industry"]
						previousClose = 0
						if "previousClose" in info:
							previousClose = info["previousClose"]
						self.SQL.InsertStock({
							'name': name,
							'ticker': ticker,
							'market_price': previousClose,
							'sector': sector,
							'industry': industry
						})
					
					self.MarketRemote.AppendStock(ticker)

					# Append threshold
					# self.AddRiskThresholdToStock(ticker)

					THIS.Node.EmitOnNodeChange({
						'event': "upload_progress",
						'data': {
							"status": "inprogress",
							"precentage": "{0:.1f}%".format(float((idx+1)/len(stocks)) * 100),
							"message": "Importing Stocks",
							"file": ""
						}
					})
				
				if False == self.SQL.StockToPortfolioExist(ticker, portfolio_id):
					self.SQL.InsertStockToPortfolio(ticker, portfolio_id)
					
		self.MarketRemote.ContinueMarket()
		self.MarketRemote.UpdateStocks()

		THIS.Node.EmitOnNodeChange({
			'event': "upload_progress",
			'data': {
				"status": "inprogress",
				"precentage": "100%",
				"message": "Importing Stocks. Done.",
				"file": ""
			}
		})
		return {
			'status': 'success'
		}

	def CreateNewPortfolioHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [CreateNewPortfolioHandler]".format(classname=self.ClassName),5)
		res = self.SQL.InsertPortfolio(payload["name"])

		return {
			"id": res
		}

	def AppendNewActionHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [AppendNewActionHandler] {0}".format(payload["action"],classname=self.ClassName),5)
		res 			= 0
		sell_ammount	= int(payload["amount"])
		buy_amount 		= 0

		risk = 2.0
		now = datetime.now()
		res = self.SQL.InsertStockHistory({
			'timestamp': 	time.time(),
			'date': 		now.strftime("%m-%d-%Y 00:00:00"),
			'ticker': 		payload["ticker"],
			'price': 		payload["price"],
			'action': 		payload["action"],
			'amount': 		payload["amount"],
			'fee': 			payload["fee"],
			'risk': 		risk
		})
		
		# Sell stock
		if payload["action"] == 1:
			pass
			# Get all buy with leftovers rows
			actions = self.SQL.GetBuyStocksWithLeftovers(payload["ticker"])
			for action in actions:
				buy_amount += int(action["leftovers"])
			
			# Check for selling action if number of stock in possetion bigger then selling
			if sell_ammount > buy_amount:
				return {
					"id": res
				}

			# Update leftovers
			for action in actions[::-1]:
				if sell_ammount == 0:
					break
				
				leftovers 	= int(action["leftovers"])
				act_id 		= int(action["id"])
				if leftovers < sell_ammount:
					# Update buy action, all action sold
					self.SQL.UpdateStockActionLeftoverById(act_id, 0)
					self.SQL.InsertStockHistorySellInfo({
						"stocks_history_sell_id": res,
						"stocks_history_buy_id": act_id,
						"quantity": leftovers
					})
					sell_ammount -= leftovers
				else:
					self.SQL.UpdateStockActionLeftoverById(act_id,leftovers - sell_ammount)
					self.SQL.InsertStockHistorySellInfo({
						"stocks_history_sell_id": res,
						"stocks_history_buy_id": act_id,
						"quantity": sell_ammount
					})
					sell_ammount = 0
		else:
			# Append threshold
			self.AddRiskThreshold(payload["ticker"].upper(), res, payload["price"], risk)

		return {
			"id": res
		}

	def GetStockHistoryHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetStockHistoryHandler] {0}".format(payload,classname=self.ClassName),5)
		
		error, data = self.SQL.GetStockHistory(payload["ticker"])
		return {
			"history": data,
			"error": error
		}
	
	def GetPortfoliosHandler(self, sock, packet):
		self.Node.LogMSG("({classname})# [GetPortfoliosHandler]".format(classname=self.ClassName),5)
		
		return {
			"portfolios": self.SQL.GetPortfolios()
		}
	
	def DownloadStockInfoHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DownloadStockInfoHandler] ({0})".format(payload["ticker"],classname=self.ClassName),5)
		info = None

		try:
			ticker = payload["ticker"]
			# Check if info can be downloaded from local DB
			info_db = self.SQL.SelectYFInfo(ticker)
			if info_db is None:
				info = self.MarketRemote.API.GetStockInfoRaw(ticker)
				self.SQL.UpdateYFInfo(ticker, json.dumps(info))
				info["price"] = info["previousClose"]
			elif info_db == "":
				info = self.MarketRemote.API.GetStockInfoRaw(ticker)
				self.SQL.UpdateYFInfo(ticker, json.dumps(info))
				info["price"] = info["previousClose"]
			else:
				info = json.loads(info_db)
				stock = self.MarketRemote.CacheDB[ticker]
				if stock is not None:
					info["price"] = stock["price"]
				else:
					info["price"] = info["previousClose"]
		except Exception as e:
			self.Node.LogMSG("({classname})# [DownloadStockInfoHandler] Exeption ({0})".format(e,classname=self.ClassName),5)

		return {
			"info": info
		}

	def DownloadStockHistoryHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		error, hist = self.MarketRemote.API.GetStockHistory(payload["ticker"], payload["period"], payload["interval"])

		if len(hist) == 0:
			return {
				"ticker": payload["ticker"]
			}

		stock_date 			= []
		stock_open 			= []
		stock_close 		= []
		stock_high 			= []
		stock_low 			= []
		stock_vol 			= []

		for stock in hist:
			stock_date.append(stock["date"])
			stock_open.append(stock["open"])
			stock_close.append(stock["close"])
			stock_high.append(stock["high"])
			stock_low.append(stock["low"])
			stock_vol.append(stock["vol"])
		
		self.BasicPrediction.SetBuffer(stock_open)
		error, output = self.BasicPrediction.Execute()
		statistics = self.StockCalulator.GetBasicStatistics(stock_close)
		
		high = output["output"]["index_high"]
		mid  = output["output"]["index_middle"]
		low  = output["output"]["index_low"]
		pmin = output["output"]["index_min"]
		pmax = output["output"]["index_max"]
		x 	 = output["output"]["x"]
		y 	 = output["output"]["y"]

		return {
			"ticker": payload["ticker"],
			"data": {
				"min": x[pmin],
				"max": x[pmax],
				"date": stock_date,
				"open": stock_open,
				"close": stock_close,
				"high": stock_high,
				"low": stock_low,
				"vol": stock_vol,
				"statistics": statistics,
				"hist_open": {
					"x": x,
					"y": y
				},
				"algo": {
					"perc_low": [x[low]]*len(hist),
					"perc_mid": [x[mid]]*len(hist),
					"perc_high": [x[high]]*len(hist)
				}
			}
		}

	def GetPortfolioStocksHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler] {0}".format(payload, classname=self.ClassName),5)

		portfolio_id = payload["portfolio_id"]

		return { 
			"stocks": self.SQL.GetStocksByPortfolioId(portfolio_id)
		}

		'''
		self.CurrentPortfolio	= int(payload["portfolio_id"])
		portfolio_earnings		= 0.0
		portfolio_investment	= 0.0
		earnings 				= 0.0
		stocks_count  			= 0
		db_stocks 				= []

		# Stock market status
		status 			= self.MarketRemote.GetMarketStatus()
		mkt_stocks 		= self.MarketRemote.GetCacheDB()
		if status["local_stock_market_ready"] is False:
			updated_stocks 	= 0
			# Get portfolio stocks
			db_stocks  		= self.SQL.GetStocksByPortfolioId(self.CurrentPortfolio)
			for db_stock in db_stocks:
				ticker = db_stock["ticker"]
				if mkt_stocks[ticker]["updated"] is True:
					updated_stocks += 1
			status["percentage"] = float("{0:.1f}".format(float(updated_stocks) / float(len(db_stocks)) * 100.0))
			return {
				"portfolio": None,
				"stocks": None,
				"status": status
			}
		else:
			# Get portfolio stocks
			db_stocks = self.SQL.GetPortfolioStocks(self.CurrentPortfolio)
			# For each stock do calculation
			stocks_in_payload 	= 0
			stocks_per_payload 	= 50
			stocks_list 		= []
			for db_stock in db_stocks:
				# For each stock in DB
				ticker = db_stock["ticker"]
				# Get stock information from cache DB
				stock = self.MarketRemote.GetStockInformation(ticker)
				if stock is not None:
					price 		= stock["price"]
					earnings 	= 0.0
					# Calculate actions min, max and summary
					if price > 0:
						if db_stock["amount_sum"] is not None and db_stock["hist_price_sum"] is not None:
							earnings = float("{0:.3f}".format(db_stock["hist_price_sum"]))
							if (price * db_stock["amount_sum"]) > 0:
								earnings = float("{0:.3f}".format(price * db_stock["amount_sum"] + db_stock["hist_price_sum"]))
							stocks_count += db_stock["amount_sum"]
							portfolio_earnings += earnings
							portfolio_investment += price * db_stock["amount_sum"]
						else:
							db_stock["amount_sum"] 	= 0.0
							db_stock["hist_min"] 	= 0.0
							db_stock["hist_max"]	= 0.0
					
					stocks_in_payload += 1
					stocks_list.append({
						"ticker":ticker,
						"name": db_stock["name"],
						"number": db_stock["amount_sum"],
						"earnings": earnings,
						"market_price": price,
						"hist_price_min": db_stock["hist_min"],
						"hist_price_max": db_stock["hist_max"],
						"statistics": {
						}
					})
				else:
					self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler] TICKER NULL {0}".format(ticker, classname=self.ClassName),5)
		
				if stocks_in_payload == stocks_per_payload:
					THIS.Node.EmitOnNodeChange({
						'event': "stock_info",
						'data': stocks_list
					})
					
					stocks_in_payload 	= 0
					stocks_list 		= []
			if stocks_in_payload != 0:
				THIS.Node.EmitOnNodeChange({
					'event': "stock_info",
					'data': stocks_list
				})

		return {
			"portfolio": {
				"name": payload["portfolio_name"],
				"companies_count": len(db_stocks),
				"stocks_count": stocks_count,
				"earnings": float("{0:.3f}".format(portfolio_earnings)),
				"investment": float("{0:.3f}".format(portfolio_investment))
			},
			"status": status
		}
		'''
	
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
		self.MarketRemote.SetLogger(self.Node.Logger)
		stocks = self.SQL.GetStocks()
		if stocks is not None:
			if len(stocks) > 0:
				for stock in stocks:
					ticker = stock["ticker"]
					# self.Node.LogMSG("({classname})# {0}".format(stock,classname=self.ClassName),5)
					self.MarketRemote.AppendStock(ticker)
					self.AddRiskThresholdToStock(ticker)
					# Get all thresholds for this ticker

					self.Node.LogMSG("({classname})# Append Thresholds to Runtime Service ...".format(classname=self.ClassName),5)
					thresholds = self.SQL.GetStockThresholds(ticker)
					if thresholds is None:
						# self.AddUpperLimitThreshold(ticker, 0.0) # UPPER
						# self.AddLowerLimitThreshold(ticker, 0.0) # LOWER
						# Insert into DB
						self.SQL.InsertStockThreshold({
							"ticker": ticker,
							"value": 0.0,
							"type": 10
						})
						self.SQL.InsertStockThreshold({
							"ticker": ticker,
							"value": 0.0,
							"type": 11
						})
					else:
						for item in thresholds:
							self.Node.LogMSG("({classname})# {0}".format(item,classname=self.ClassName),5)
							if item["type"] == 10:
								if item["enabled"] == 1:
									self.AddUpperLimitThreshold(ticker, item["value"]) # UPPER
							elif item["type"] == 11:
								if item["enabled"] == 1:
									self.AddLowerLimitThreshold(ticker, item["value"]) # LOWER
							else:
								pass
		
		self.Node.LogMSG("({classname})# Starting Market Runtime Service ...".format(classname=self.ClassName),5)
		# Start market service
		self.MarketRemote.Start()

		# Create file system for storing videos
		if not os.path.exists(self.LocalStoragePath):
			os.makedirs(self.LocalStoragePath)
		
		# Uploader
		self.Uploader = MkSFileUploader.Manager(self)
		self.Uploader.SetUploadPath(os.path.join(".",self.LocalStoragePath))
		self.Uploader.Run()

		# self.PotfolioHistoryChangeWorker(0)
		# self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Node Started", "")
	
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
	THIS.MarketRemote.Stop()
	THIS.Uploader.Stop()
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
