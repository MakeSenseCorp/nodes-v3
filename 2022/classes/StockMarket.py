#!/usr/bin/python
import os
import sys
import signal
import json
import time
import urllib.request
import requests

from classes import StockMarketRemote
from classes import StockDataBase

class StockMarket():
	def __init__(self, node, market):
		self.ClassName 	= "StockMarket"
		self.Node	 	= node
		self.Market 	= market
		self.SQL		= StockDataBase.StockDB("stocks.db")
	
	def BindHandler(self):
		# Handlers
		self.Node.ApplicationRequestHandlers['get_market_stocks'] 			= self.GetMarketStocksHandler
		self.Node.ApplicationRequestHandlers['get_portfolio_statistics'] 	= self.GetPortfolioStatistics
	
	def GetMarketStocksHandler(self, sock, packet):
		self.Node.LogMSG("({classname})# [GetMarketStocksHandler]".format(classname=self.ClassName),5)

		# Stock market status
		#status 		= self.Market.GetMarketStatus()
		#mkt_stocks 	= self.Market.GetCacheDB()
		#if status["local_stock_market_ready"] is False:
		#	self.Node.LogMSG("({classname})# [GetMarketStocksHandler] Local Market DB is NOT ready yet.".format(classname=self.ClassName),5)
		#	updated_stocks 	= 0
		#	# Get portfolio stocks
		#	db_stocks  		= self.SQL.GetStocksByPortfolioId(self.CurrentPortfolio)
		#	for db_stock in db_stocks:
		#		ticker = db_stock["ticker"]
		#		if mkt_stocks[ticker]["updated"] is True:
		#			updated_stocks += 1
		#	status["percentage"] = float("{0:.1f}".format(float(updated_stocks) / float(len(db_stocks)) * 100.0))
		#	return {
		#		"status": status
		#	}

		# Get all stocks
		db_stocks = self.SQL.GetPortfolioStocks(0)
		# For each stock do calculation
		stocks_in_payload 			= 0
		stocks_per_payload 			= 50
		stocks_list 				= []
		stocks_count  				= 0
		total_investment 			= 0.0
		total_current_investment 	= 0.0
		for db_stock in db_stocks:
			# For each stock in DB
			ticker = db_stock["ticker"]
			# Get stock information from cache DB
			stock = self.Market.GetStockInformation(ticker)
			if stock is not None:
				market_price 	= stock["price"]
				earnings 		= 0.0
				# Calculate actions min, max and summary
				try:
					if market_price > 0:
						if db_stock["amount_sum"] is not None and db_stock["hist_price_sum"] is not None:
							# earnings = float("{0:.3f}".format(db_stock["hist_price_sum"]))
							if (market_price * db_stock["amount_sum"]) > 0 or db_stock["amount_sum"] == 0:
								# TODO - market_price BUG (unsupported operand type(s) for *: 'int' and 'NoneType')
								earnings = float("{0:.3f}".format(market_price * db_stock["amount_sum"] + db_stock["hist_price_sum"]))
								total_current_investment += market_price * db_stock["amount_sum"]
								total_investment += db_stock["hist_price_sum"]
							stocks_count += db_stock["amount_sum"]
						else:
							db_stock["amount_sum"] 	= 0.0
							db_stock["hist_min"] 	= 0.0
							db_stock["hist_max"]	= 0.0
				except Exception as e:
					self.Node.LogMSG("({classname})# [EXCEPTION] GetMarketStocksHandler - Calculation {0} {1}".format(ticker,str(e),classname=self.ClassName), 5)
				
				# Get all portfolios binded to this ticker
				stock_portfolios = self.SQL.GetStockPortfolios(ticker)
				# Get price from day before
				prev_market_price = market_price
				if "prev_market_price" in stock:
					prev_market_price = stock["prev_market_price"]

				stocks_in_payload += 1
				try:
					stocks_list.append({
						"ticker":					ticker,
						"portfolios": 				stock_portfolios,
						"name": 					db_stock["name"],
						"number": 					db_stock["amount_sum"],
						"earnings": 				earnings,
						"total_investment": 		total_investment,
						"total_current_investment": total_current_investment,
						"market_price": 			market_price,
						"prev_market_price": 		prev_market_price,
						"hist_price_min": 			db_stock["hist_min"],
						"hist_price_max": 			db_stock["hist_max"],
						"statistics": 				stock["statistics"],
						"thresholds": 				stock["thresholds"],
						"predictions": 				stock["predictions"]
					})
				except Exception as e:
					# BUG #1 - unsupported operand type(s) for *: 'int' and 'NoneType'
					self.Node.LogMSG("({classname})# [EXCEPTION] GetMarketStocksHandler - Append stock {0} {1} {2}".format(ticker,str(e),classname=self.ClassName), 5)
			else:
				self.Node.LogMSG("({classname})# [GetMarketStocksHandler] TICKER NULL {0}".format(ticker, classname=self.ClassName),5)
	
			if stocks_in_payload == stocks_per_payload:
				self.Node.EmitOnNodeChange({
					'event': "stock_info",
					'data': stocks_list
				})
				
				stocks_in_payload 	= 0
				stocks_list 		= []
		if stocks_in_payload != 0:
			self.Node.EmitOnNodeChange({
				'event': "stock_info",
				'data': stocks_list
			})
		
		return {
			"status": True
		}
	
	def GetPortfolioStatistics(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetPortfolioStatistics] {0}".format(payload, classname=self.ClassName),5)

		potrfolio_id 				= payload["portfolio_id"]
		earnings					= 0.0
		stocks_count  				= 0
		total_investment 			= 0.0
		total_current_investment 	= 0.0
		total_stock_diff 			= 0.0
		# Get all stocks
		db_stocks = self.SQL.GetPortfolioStocks(potrfolio_id)
		for db_stock in db_stocks:
			# For each stock in DB
			ticker = db_stock["ticker"]
			# Get stock information from cache DB
			stock = self.Market.GetStockInformation(ticker)
			if stock is not None:
				# Curent price
				market_price 	= stock["price"]
				# Get price from day before
				prev_market_price = market_price
				if "prev_market_price" in stock:
					prev_market_price = stock["prev_market_price"]
				# Calculate earnings and other
				try:
					if market_price > 0:
						if db_stock["amount_sum"] is not None and db_stock["hist_price_sum"] is not None:
							if (market_price * db_stock["amount_sum"]) > 0 or db_stock["amount_sum"] == 0:
								# TODO - market_price BUG (unsupported operand type(s) for *: 'int' and 'NoneType')
								earnings += float("{0:.3f}".format(market_price * db_stock["amount_sum"] + db_stock["hist_price_sum"]))
							stocks_count += db_stock["amount_sum"]
							total_current_investment += market_price * db_stock["amount_sum"]
							total_investment += db_stock["hist_price_sum"]
						else:
							pass
						total_stock_diff += (market_price - prev_market_price)
					else:
						pass
				except Exception as e:
					self.Node.LogMSG("({classname})# [EXCEPTION] GetPortfolioStatistics {0} {1}".format(ticker,str(e),classname=self.ClassName), 5)
				
		return {
			"portfolio_id": 			potrfolio_id,
			"stocks_count":				stocks_count,
			"earnings": 				earnings,
			"total_investment": 		total_investment,
			"total_current_investment": total_current_investment,
			"total_stock_diff":			total_stock_diff
		}