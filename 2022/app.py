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
			'amount': payload["amount"]
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
					price = stock["price"]
					if price > 0:
						earnings = float("{0:.3f}".format(price * db_stock["amount_sum"] - db_stock["hist_price_sum"]))
						portfolio_earnings += earnings
						portfolio_investment += price * db_stock["amount_sum"]

					data = stock["5D"]
					w_min, w_max = self.Market.CalculateMinMax(data)
					w_slope, w_b, w_r2 = self.Market.GetRegressionLineStatistics(data)
					w_var, w_std = self.Market.GetBasicStatistics(data)

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
