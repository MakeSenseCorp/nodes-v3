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

from classes import StockMarket
from classes import StockDataBase

class Context():
	def __init__(self, node):
		self.ClassName					= "Apllication"
		self.Timer						= MkSScheduling.TimeSchedulerThreadless()
		self.Node						= node
		self.File						= MkSFile.File()
		self.Market 					= StockMarket.StockMarket()
		self.SQL 						= StockDataBase.StockDB("stocks.db")
		# States
		self.States = {
		}
		# Handlers
		self.Node.ApplicationRequestHandlers	= {
			'get_sensor_info':			self.GetSensorInfoHandler,
			'get_portfolios':			self.GetPortfoliosHandler,
			'get_portfolio_stocks':		self.GetPortfolioStocksHandler,
			'get_portfolio_statistics':	self.GetPortfolioStatistics,
			'get_stock_history':		self.GetStockHistoryHandler,
			'append_new_action':		self.AppendNewActionHandler,
			'create_new_portfolio':		self.CreateNewPortfolioHandler,
			'import_stocks':			self.ImportStocksHandler,
			'export_stocks': 			self.ExportStocksHandler,
			'upload_file':				self.Request_UploadFileHandler,
			'load_csv':					self.LoadCSVHandler,
			'download_stock_history':	self.DownloadStockHistoryHandler,
			'download_stock_info':		self.DownloadStockInfoHandler,
			'get_db_stocks':			self.GetDBStocksHandler,
			'get_stock_portfolios':		self.GetStockPortfolios,
			'set_stock_portfolios':		self.SetStockPortfolios,
			'delete_portfolio':			self.DeletePortfolioHandler,
			'db_insert_stock':			self.DBInsertStockHandler,
			'db_delete_stock':			self.DBDeleteStockHandler,
			'get_market_stocks':		self.GetMarketStocksHandler,
			'db_delete_action':			self.DBDeleteActionHandler,
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
		self.UploadLocker 				= threading.Lock()
		self.LocalStoragePath 			= "import"

		self.Timer.AddTimeItem(10, self.PrintConnections)
		self.Market.FullLoopPerformedCallback 				= self.FullLoopPerformedEvent
		# self.Market.StockChangeCallback 					= self.StockChangeEvent
		self.Market.FirstRunDoneCallback					= self.FirstRunDoneEvent
		self.Market.StockMarketOpenCallback					= self.StockMarketOpenEvent
		self.Market.StockMarketCloseCallback				= self.StockMarketCloseEvent
		# self.Market.StockSimplePredictionChangeCallback 	= self.StockSimplePredictionChangeEvent
		self.CurrentPortfolio 			= 0
	
	def StockSimplePredictionChangeEvent(self, data):
		self.Node.LogMSG("({classname})# [StockSimplePredictionChangeEvent]".format(classname=self.ClassName),5)
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
					<td><span>Previouse Prediction</span></td>
					<td><span>{2}</span></td>
				</tr>
				<tr>
					<td><span>Current Prediction</span></td>
					<td><span>{3}</span></td>
				</tr>
			</table>
		'''.format(data["ticker"], data["price"], data["pred_prev"], data["pred_curr"])
		self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Prediction Change", html)

	def StockMarketCloseEvent(self):
		pass

	def StockMarketOpenEvent(self):
		pass

	def FirstRunDoneEvent(self):
		self.Node.LogMSG("({classname})# [FirstRunDoneEvent]".format(classname=self.ClassName),5)
		stocks = self.Market.GetStocks()
		html_rows = ""
		for ticker in stocks:
			stock = stocks[ticker]

			html_rows += '''
				<tr>
					<td><a href="#">{0}</a></td>
					<td>{1}</td>
					<td>{2}</td>
				</tr>
			'''.format(stock["ticker"], stock["price"],stock["predictions"]["basic_action"])

		html = "<table>{0}</table>".format(html_rows)
		self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Node Started", html)

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

	def AddRiskThreshold(self, ticker, act_id, price, risk):
		try:
			'''
				1 - Below
				2 - Equal
				3 - Above
			'''
			self.Market.AppendThreshold(ticker, {
				"stock_action_id": act_id,
				"value": float(price) * ((100.0 - float(risk)) / 100.0),
				"type": 1,
				"activated": False
			})
		except Exception as e:
			print(e)

	def GetMarketStocksHandler(self, sock, packet):
		self.Node.LogMSG("({classname})# [GetMarketStocksHandler]".format(classname=self.ClassName),5)

		# Stock market status
		status 		= self.Market.GetMarketStatus()
		mkt_stocks 	= self.Market.GetStocks()
		if status["local_stock_market_ready"] is False:
			updated_stocks 	= 0
			# Get portfolio stocks
			db_stocks  		= self.SQL.GetStocksByProfile(self.CurrentPortfolio)
			for db_stock in db_stocks:
				ticker = db_stock["ticker"]
				if mkt_stocks[ticker]["updated"] is True:
					updated_stocks += 1
			status["percentage"] = float("{0:.1f}".format(float(updated_stocks) / float(len(db_stocks)) * 100.0))
			return {
				"status": status
			}
		# Get all stocks
		db_stocks = self.SQL.GetPortfolioStocks(0)
		# For each stock do calculation
		stocks_in_payload 	= 0
		stocks_per_payload 	= 50
		stocks_list 		= []
		stocks_count  		= 0
		for db_stock in db_stocks:
			# For each stock in DB
			ticker = db_stock["ticker"]
			# Get stock information from cache DB
			stock = self.Market.GetStockInformation(ticker)
			if stock is not None:
				warning 		= 0
				market_price 	= stock["price"]
				earnings 		= 0.0
				# Calculate actions min, max and summary
				if market_price > 0:
					if db_stock["amount_sum"] is not None and db_stock["hist_price_sum"] is not None:
						# earnings = float("{0:.3f}".format(db_stock["hist_price_sum"]))
						if (market_price * db_stock["amount_sum"]) > 0 or db_stock["amount_sum"] == 0:
							earnings = float("{0:.3f}".format(market_price * db_stock["amount_sum"] - db_stock["hist_price_sum"]))
						stocks_count += db_stock["amount_sum"]
					else:
						db_stock["amount_sum"] 	= 0.0
						db_stock["hist_min"] 	= 0.0
						db_stock["hist_max"]	= 0.0
				
				if "warning" in stock["5D_statistics"] and "warning" in stock["1MO_statistics"]:
					warning = stock["5D_statistics"]["warning"] & stock["1MO_statistics"]["warning"]
				
				stocks_in_payload += 1
				stocks_list.append({
					"ticker":ticker,
					"portfolio_id": db_stock["portfolio_id"],
					"name": db_stock["name"],
					"number": db_stock["amount_sum"],
					"earnings": earnings,
					"total_investment": db_stock["hist_price_sum"],
					"total_current_investment": market_price * db_stock["amount_sum"],
					"market_price": market_price,
					"hist_price_min": db_stock["hist_min"],
					"hist_price_max": db_stock["hist_max"],
					"warning": warning,
					"statistics": {
						"weekly": stock["5D_statistics"],
						"monthly": stock["1MO_statistics"]
					},
					"thresholds": stock["thresholds"],
					"predictions": stock["predictions"]
				})
			else:
				self.Node.LogMSG("({classname})# [GetMarketStocksHandler] TICKER NULL {0}".format(ticker, classname=self.ClassName),5)
	
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
			"status": status
		}

	def StockChangeEvent(self, stock):
		self.Node.LogMSG("({classname})# [StockChangeEvent]".format(classname=self.ClassName),5)
		warning 				= 0
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
			
			if "warning" in stock["5D_statistics"] and "warning" in stock["1MO_statistics"]:
				warning = stock["5D_statistics"]["warning"] & stock["1MO_statistics"]["warning"]
			
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
						"warning": warning,
						"statistics": {
							"weekly": stock["5D_statistics"],
							"monthly": stock["1MO_statistics"]
						}
					} 	
				]
			})
		except Exception as e:
			self.Node.LogMSG("({classname})# [StockChangeEvent] ERROR {0} {1}".format(ticker,e,classname=self.ClassName),5)

	def DBDeleteStockHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DBDeleteStockHandler] {0}".format(payload,classname=self.ClassName),5)
		self.SQL.DeleteStock(payload["ticker"])
		self.Market.RemoveStock(payload["ticker"])
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
		self.Market.RemoveThresholdByStockActionId(ticker, del_act_id)

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
		# Check if stock already in the DB
		if self.SQL.StockExist(payload["ticker"]) is False:
			info = self.Market.GetStockInfoRaw(payload["ticker"])
			self.Node.LogMSG("({classname})# [DBInsertStockHandler] {0} Append to stock DB".format(payload,classname=self.ClassName),5)
			self.SQL.InsertStock({
				'name': info["shortName"],
				'ticker': payload["ticker"],
				'market_price': self.CheckForDict(info["previousClose"], "previousClose"),
				'sector': info["sector"],
				'industry': info["industry"]
			})
			self.Node.LogMSG("({classname})# [DBInsertStockHandler] {0} Append to stock monitoring".format(payload,classname=self.ClassName),5)
			# Append to stock monitoring
			self.Market.AppendStock({
				"ticker": 	payload["ticker"].upper(),
				"price": 	self.CheckForDict(info["previousClose"], "previousClose"),
				"1MO": 		None,
				"5D": 		None,
				"updated": 	False,
				"pulled": 	False
			})
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
		self.Market.PauseMarket()
		
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
						info = self.Market.GetStockInfoRaw(ticker)
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
					
					self.Market.AppendStock({
						"ticker": 	ticker,
						"price": 	0,
						"1MO": 		None,
						"5D": 		None,
						"updated": 	False,
						"pulled": 	False
					})

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
					
		self.Market.ContinueMarket()
		self.Market.UpdateStocks()

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
		
		return {
			"history": self.SQL.GetStockHistory(payload["ticker"])
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
			info = self.Market.GetStockInfoRaw(payload["ticker"])
		except Exception as e:
			self.Node.LogMSG("({classname})# [DownloadStockInfoHandler] Exeption ({0})".format(e,classname=self.ClassName),5)

		return {
			"info": info
		}

	def DownloadStockHistoryHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		hist = self.Market.GetStock(payload["ticker"], payload["period"], payload["interval"])

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
		stock_regression 	= []
		w_slope, w_b, w_r2 = self.Market.GetRegressionLineStatistics(hist)
		for idx in range(len(hist)):
			stock_regression.append(w_slope*idx+w_b)

		for stock in hist:
			stock_date.append(stock["date"])
			stock_open.append(stock["open"])
			stock_close.append(stock["close"])
			stock_high.append(stock["high"])
			stock_low.append(stock["low"])
			stock_vol.append(stock["vol"])
		
		hist_open_y, hist_open_x = self.Market.CreateHistogram(stock_open, 25)
		pmin, low, mid, high, pmax = self.Market.CalculatePercentile(0.15, 0.85, hist_open_y)
		# pmin, pmax = self.Market.FindMaxMin(stock_open)
		#self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler] {0} {1}".format(hist_open_x[low], hist_open_x[high], classname=self.ClassName),5)
		return {
			"ticker": payload["ticker"],
			"data": {
				"min": hist_open_x[pmin],
				"max": hist_open_x[pmax],
				"date": stock_date,
				"open": stock_open,
				"close": stock_close,
				"high": stock_high,
				"low": stock_low,
				"vol": stock_vol,
				"regression": stock_regression,
				"hist_open": {
					"x": hist_open_x,
					"y": hist_open_y
				},
				"algo": {
					"perc_low": [hist_open_x[low]]*len(hist),
					"perc_mid": [hist_open_x[mid]]*len(hist),
					"perc_high": [hist_open_x[high]]*len(hist)
				}
			}
		}

	def GetPortfolioStatistics(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler] {0}".format(payload, classname=self.ClassName),5)

		potrfolio_id = payload["portfolio_id"]
		return {
			"portfolio_id": potrfolio_id
		}

	def GetPortfolioStocksHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler] {0}".format(payload, classname=self.ClassName),5)

		self.CurrentPortfolio	= int(payload["portfolio_id"])
		portfolio_earnings		= 0.0
		portfolio_investment	= 0.0
		earnings 				= 0.0
		stocks_count  			= 0
		db_stocks 				= []

		# Stock market status
		status 			= self.Market.GetMarketStatus()
		mkt_stocks 		= self.Market.GetStocks()
		if status["local_stock_market_ready"] is False:
			updated_stocks 	= 0
			# Get portfolio stocks
			db_stocks  		= self.SQL.GetStocksByProfile(self.CurrentPortfolio)
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
				stock = self.Market.GetStockInformation(ticker)
				if stock is not None:
					warning 	= 0
					price 		= stock["price"]
					earnings 	= 0.0
					# Calculate actions min, max and summary
					if price > 0:
						if db_stock["amount_sum"] is not None and db_stock["hist_price_sum"] is not None:
							earnings = float("{0:.3f}".format(db_stock["hist_price_sum"]))
							if (price * db_stock["amount_sum"]) > 0:
								earnings = float("{0:.3f}".format(price * db_stock["amount_sum"] - db_stock["hist_price_sum"]))
							stocks_count += db_stock["amount_sum"]
							portfolio_earnings += earnings
							portfolio_investment += price * db_stock["amount_sum"]
						else:
							db_stock["amount_sum"] 	= 0.0
							db_stock["hist_min"] 	= 0.0
							db_stock["hist_max"]	= 0.0
					
					if "warning" in stock["5D_statistics"] and "warning" in stock["1MO_statistics"]:
						warning = stock["5D_statistics"]["warning"] & stock["1MO_statistics"]["warning"]
					
					stocks_in_payload += 1
					stocks_list.append({
						"ticker":ticker,
						"name": db_stock["name"],
						"number": db_stock["amount_sum"],
						"earnings": earnings,
						"market_price": price,
						"hist_price_min": db_stock["hist_min"],
						"hist_price_max": db_stock["hist_max"],
						"warning": warning,
						"statistics": {
							"weekly": stock["5D_statistics"],
							"monthly": stock["1MO_statistics"]
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
		self.Market.SetLogger(self.Node.Logger)
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
					self.AddRiskThresholdToStock(stock["ticker"])
		self.Market.Start()

		# Create file system for storing videos
		if not os.path.exists(self.LocalStoragePath):
			os.makedirs(self.LocalStoragePath)
		
		# Uploader
		self.Uploader = MkSFileUploader.Manager(self)
		self.Uploader.SetUploadPath(os.path.join(".",self.LocalStoragePath))
		self.Uploader.Run()

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
	THIS.Market.Stop()
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
