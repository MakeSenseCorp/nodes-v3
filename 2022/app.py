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
			'get_stock_history':		self.GetStockHistoryHandler,
			'append_new_action':		self.AppendNewActionHandler,
			'create_new_portfolio':		self.CreateNewPortfolioHandler,
			'import_stocks':			self.ImportStocksHandler,
			'export_stocks': 			self.ExportStocksHandler,
			'upload_file':				self.Request_UploadFileHandler,
			'load_csv':					self.LoadCSVHandler,
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
		self.Market.FullLoopPerformedCallback = self.FullLoopPerformedEvent
	
	def FullLoopPerformedEvent(self):
		pass

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
		
		portfolio_id = 1
		tickers = self.SQL.GetTickers()
		if payload["portfolio_checked"] is True:
			if False == self.SQL.PortfolioExist(payload["portfolio_name"]):
				self.Node.LogMSG("({classname})# [ImportStocksHandler] Create portfolio ({0})".format(payload["portfolio_name"], classname=self.ClassName),5)
				portfolio_id = self.SQL.InsertPortfolio(payload["portfolio_name"])
		
		stocks = payload["stocks"]
		for item in stocks:
			date 	= item["date"].replace("/","-")
			ticker 	= item["ticker"]
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

				if ticker not in tickers:
					self.SQL.InsertStock({
						"name": "",
						"ticker": ticker,
						"sector": "",
						"industry": "",
						"market_price": float(price)
					})
					tickers = self.SQL.GetTickers()
				
				if False == self.SQL.StockToPortfolioExist(ticker, portfolio_id):
					self.SQL.InsertStockToPortfolio(ticker, portfolio_id)

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
		self.Node.LogMSG("({classname})# [AppendNewActionHandler]".format(classname=self.ClassName),5)

		now = datetime.now()
		res = self.SQL.InsertStockHistory({
			'timestamp': time.time(),
			'date': now.strftime("%m-%d-%Y 00:00:00"),
			'ticker': payload["ticker"],
			'price': payload["price"],
			'action': payload["action"],
			'amount': payload["amount"],
			'fee': payload["fee"]
		})

		return {
			"id": res
		}

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
		self.Node.LogMSG("({classname})# [GetPortfolioStocksHandler] {0}".format(payload["portfolio_id"], classname=self.ClassName),5)
		
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
					warning = 0
					price = stock["price"]
					if price > 0:
						earnings = float("{0:.3f}".format(price * db_stock["amount_sum"] - db_stock["hist_price_sum"]))
						portfolio_earnings += earnings
						portfolio_investment += price * db_stock["amount_sum"]

					w_min = w_max = w_slope = w_b = w_r2 = w_var = w_std = 0
					data = stock["5D"]
					if len(data) > 0:
						w_min, w_max = self.Market.CalculateMinMax(data)
						w_slope, w_b, w_r2 = self.Market.GetRegressionLineStatistics(data)
						w_var, w_std = self.Market.GetBasicStatistics(data)
					else:
						warning = 1

					m_min = m_max = m_slope = m_b = m_r2 = m_var = m_std = 0
					data = stock["1MO"]
					if len(data) > 0:
						m_min, m_max = self.Market.CalculateMinMax(data)
						m_slope, m_b, m_r2 = self.Market.GetRegressionLineStatistics(data)
						m_var, m_std = self.Market.GetBasicStatistics(data)
						if math.isnan(m_min) is True:
							m_min = 0
						if math.isnan(m_max) is True:
							m_max = 0
						if math.isnan(m_slope) is True:
							m_slope = 0
						if math.isnan(m_b) is True:
							m_b = 0
						if math.isnan(m_r2) is True:
							m_r2 = 0
						if math.isnan(m_var) is True:
							m_var = 0
						if math.isnan(m_std) is True:
							m_std = 0
					else:
						warning = 1
					
					stocks.append({
						"ticker":ticker,
						"name": db_stock["name"],
						"number": db_stock["amount_sum"],
						"earnings": earnings,
						"market_price": price,
						"hist_price_min": db_stock["hist_min"],
						"hist_price_max": db_stock["hist_max"],
						"warning": warning,
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
		portfolio_earnings   = float("{0:.3f}".format(portfolio_earnings))
		portfolio_investment = float("{0:.3f}".format(portfolio_investment))
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
		self.Market.Start()

		# Create file system for storing videos
		if not os.path.exists(self.LocalStoragePath):
			os.makedirs(self.LocalStoragePath)
		
		# Uploader
		self.Uploader = MkSFileUploader.Manager(self)
		self.Uploader.SetUploadPath(os.path.join(".",self.LocalStoragePath))
		self.Uploader.Run()
	
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
