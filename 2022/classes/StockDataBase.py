#!/usr/bin/python
import os
import sys
import time
import base64
import datetime
from datetime import date

import math
import sqlite3

class StockDB():
	def __init__(self, path):
		path = os.path.join("", path)
		self.ClassName	= "StockDB"
		self.DB 		= sqlite3.connect(path, check_same_thread=False)
		self.CURS		= self.DB.cursor()

		self.BuildSchema()
	
	def BuildSchema(self):
		'''
			leftovers - How many stock still available for this buy.
		'''
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_history" (
							"id"		INTEGER PRIMARY KEY AUTOINCREMENT,
							"timestamp"	REAL NOT NULL,
							"date"		TEXT NOT NULL,
							"ticker"	TEXT NOT NULL,
							"price"		REAL NOT NULL,
							"action"	INTEGER NOT NULL,
							"amount"	INTEGER,
							"fee"		REAL,
							"leftovers" INTEGER,
							"risk"		REAL
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_info" (
							"id"			INTEGER PRIMARY KEY AUTOINCREMENT,
							"name"			TEXT NOT NULL,
							"ticker"		TEXT NOT NULL,
							"sector"		TEXT,
							"industry"		TEXT,
							"market_price"	REAL,
							"yf_info"		TEXT
						);''')
				
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "portfolios" (
							"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
							"name"	TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stock_to_portfolio" (
							"ticker"		TEXT NOT NULL,
							"portfolio_id"	INTEGER NOT NULL
						);''')

		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "actions" (
							"id"	INTEGER,
							"name"	TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_history_sell_info" (
							"id"						INTEGER PRIMARY KEY AUTOINCREMENT,
							"stocks_history_sell_id" 	INTEGER,
							"stocks_history_buy_id" 	INTEGER,
							"quantity"					INTEGER
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_history_actions" (
							"id"						INTEGER PRIMARY KEY AUTOINCREMENT,
							"action" 					INTEGER,
							"timestamp" 				REAL,
							"info"						TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_thresholds" (
							"id"						INTEGER PRIMARY KEY AUTOINCREMENT,
							"ticker" 					TEXT,
							"value" 					REAL,
							"type"						INTEGER
						);''')

		self.Init()

	def Init(self):
		self.CURS.execute("SELECT * FROM actions WHERE id=1")
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return
		
		self.CURS.execute("SELECT * FROM portfolios WHERE id=1")
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return
		
		self.CURS.execute("INSERT INTO actions (id,name) VALUES(-1,'BUY')")
		self.CURS.execute("INSERT INTO actions (id,name) VALUES(1,'SELL')")
		self.CURS.execute("INSERT INTO portfolios (id,name) VALUES(1,'Watch')")
		self.DB.commit()

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
	
	def GetStockPortfolios(self, ticker):
		query = "SELECT portfolio_id FROM stock_to_portfolio WHERE ticker='{0}'".format(ticker.upper())
		self.CURS.execute(query)
		
		portfolios = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				portfolios.append(row[0])
		return portfolios
	
	def GetStocksByProfile(self, id):
		if 0 == id:
			query = '''
				SELECT * FROM stocks_info 
				LEFT JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			'''
		else:
			query = '''
				SELECT * FROM stocks_info 
				LEFT JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
				WHERE stock_to_portfolio.portfolio_id = {0}
			'''.format(id)
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"id":			row[0],
					"name": 		row[1],
					"ticker": 		row[2],
					"sector": 		row[3],
					"industry": 	row[4],
					"market_price": row[5],
					"yf_info":		row[6]
				})
		return stocks
	
	def GetTickers(self):
		query = "SELECT * FROM stocks_info"
		self.CURS.execute(query)
		
		tickers = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				tickers.append(row[2])
		return tickers

	def GetStockExtetendedInfo(self, ticker):
		query = '''
		SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, hist_max, hist_min, stocks_info.yf_info FROM stocks_info 
		LEFT JOIN (
			SELECT ticker, ABS(SUM(price * action * amount)) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
			FROM stocks_history 
			GROUP BY ticker) as hist ON hist.ticker == stocks_info.ticker
		LEFT JOIN (
			SELECT ticker, MAX(price) as hist_max, MIN(price) as hist_min
			FROM stocks_history
			WHERE action == -1
			GROUP BY ticker) as tbl_actions ON tbl_actions.ticker == stocks_info.ticker
		WHERE stocks_info.ticker = '{0}'
		'''.format(ticker)

		self.CURS.execute(query)
		rows = self.CURS.fetchall()
		
		if len(rows) > 0:
			return {
					"ticker": 			rows[0][0],
					"name": 			rows[0][1],
					"market_price": 	rows[0][2],
					"curr_price_sum": 	rows[0][3],
					"hist_price_sum": 	rows[0][4],
					"amount_sum": 		rows[0][5],
					"hist_max": 		rows[0][6],
					"hist_min": 		rows[0][7],
					"yf_info":			rows[0][8]
				}
		return None

	def GetPortfolioStocks(self, id):
		stocks = []
		if 0 == id:
			query = '''
			SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, stock_to_portfolio.portfolio_id, hist_max, hist_min, stocks_info.yf_info FROM stocks_info 
			LEFT JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			LEFT JOIN (
				SELECT ticker, SUM(price * action * amount) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
				FROM stocks_history 
				GROUP BY ticker) as hist ON hist.ticker == stocks_info.ticker
			LEFT JOIN (
				SELECT ticker, MAX(price) as hist_max, MIN(price) as hist_min
				FROM stocks_history
				WHERE action == -1
				GROUP BY ticker) as tbl_actions ON tbl_actions.ticker == stocks_info.ticker
			GROUP BY stocks_info.ticker
			'''
		else:
			query = '''
			SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, stock_to_portfolio.portfolio_id, hist_max, hist_min, stocks_info.yf_info FROM stocks_info 
			LEFT JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			LEFT JOIN (
				SELECT ticker, SUM(price * action * amount) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
				FROM stocks_history 
				GROUP BY ticker) as hist ON hist.ticker == stocks_info.ticker
			LEFT JOIN (
				SELECT ticker, MAX(price) as hist_max, MIN(price) as hist_min
				FROM stocks_history
				WHERE action == -1
				GROUP BY ticker) as tbl_actions ON tbl_actions.ticker == stocks_info.ticker
			WHERE stock_to_portfolio.portfolio_id == {0}
			GROUP BY stocks_info.ticker
			'''.format(id)
		self.CURS.execute(query)
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"ticker": 			row[0],
					"name": 			row[1],
					"market_price": 	row[2],
					"curr_price_sum": 	row[3],
					"hist_price_sum": 	row[4],
					"amount_sum": 		row[5],
					"portfolio_id": 	row[6],
					"hist_max": 		row[7],
					"hist_min": 		row[8],
					"yf_info": 			row[9]
				})
		return stocks
	
	def GetStockHistory(self, ticker):
		query = '''
			SELECT stocks_history.id, timestamp, date, price, amount, name, action, fee FROM stocks_history
			INNER JOIN actions ON actions.id == stocks_history.action
			WHERE stocks_history.ticker == "{0}"
		'''.format(ticker)
		self.CURS.execute(query)
		
		error 	= False
		stocks 	= []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"id": 		 	row[0],
					"timestamp": 	row[1],
					"date": 	 	row[2],
					"price": 	 	row[3],
					"amount": 	 	row[4],
					"action_name": 	row[5],
					"action": 	 	row[6],
					"fee": 			row[7]
				})
		return error, stocks
	
	def GetBuyStocksWithLeftovers(self, ticker):
		query = '''
			SELECT stocks_history.id, timestamp, date, price, amount, name, action, fee, leftovers, risk FROM stocks_history
			INNER JOIN actions ON actions.id == stocks_history.action
			WHERE stocks_history.leftovers > 0 AND stocks_history.action = -1 AND ticker = '{0}'
		'''.format(ticker)
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"id": 		 	row[0],
					"timestamp": 	row[1],
					"date": 	 	row[2],
					"price": 	 	row[3],
					"amount": 	 	row[4],
					"action_name": 	row[5],
					"action": 	 	row[6],
					"fee": 			row[7],
					"leftovers":	row[8],
					"risk":			row[9]
				})
		else:
			return None
		return stocks
	
	def StockToPortfolioExist(self, ticker, portfolio_id):
		query = "SELECT * FROM stock_to_portfolio WHERE ticker = '{0}' AND portfolio_id = {1}".format(ticker, portfolio_id)
		self.CURS.execute(query)

		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return True
		
		return False
	
	def PortfolioExist(self, portfolio_name):
		query = "SELECT * FROM portfolios WHERE name = '{0}'".format(portfolio_name)
		self.CURS.execute(query)
		
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return True
		
		return False
	
	# ---- STOCKS ----

	def StockExist(self, ticker):
		if self.GetStock(ticker) is not None:
			return True
		return False
	
	def GetStock(self, ticker):
		query = "SELECT * FROM stocks_info WHERE ticker='{0}'".format(ticker.upper())
		self.CURS.execute(query)
		
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return rows[0]
		return None

	def GetStocks(self):
		query = "SELECT * FROM stocks_info"
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"id":			row[0],
					"name": 		row[1],
					"ticker": 		row[2],
					"sector": 		row[3],
					"industry": 	row[4],
					"market_price": row[5],
					"yf_info":		row[6]
				})
		return stocks
	
	def InsertStock(self, stock):
		query = '''
			INSERT INTO stocks_info (id,name,ticker,sector,industry,market_price,yf_info)
			VALUES (NULL,'{0}','{1}','{2}','{3}',{4},'')
		'''.format(stock["name"],stock["ticker"].upper(),stock["sector"],stock["industry"],stock["market_price"])
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def DeleteStock(self, ticker):
		self.CURS.execute('''
			DELETE FROM stock_to_portfolio
			WHERE ticker = '{0}'
		'''.format(ticker))
		self.DB.commit()

		self.CURS.execute('''
			DELETE FROM stocks_info
			WHERE ticker = '{0}'
		'''.format(ticker))
		self.DB.commit()
	
	# ---- STOCKS ----

	
	# ---- THRESHOLDS ----

	def GetStockThresholds(self, ticker):
		query = "SELECT * FROM stocks_thresholds WHERE ticker='{0}'".format(ticker.upper())
		self.CURS.execute(query)
		
		thresholds = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				thresholds.append({
					"id":		row[0],
					"ticker": 	row[1],
					"value": 	row[2],
					"type": 	row[3]
				})
			return thresholds
		return None
	
	def InsertStockThreshold(self, threshold):
		query = '''
			INSERT INTO stocks_thresholds (id,ticker,value,type)
			VALUES (NULL,'{0}',{1},{2})
		'''.format(threshold["ticker"].upper(),threshold["value"],threshold["type"])
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def UpdateStockThreshold(self, id, value):
		query = '''
			UPDATE stocks_thresholds
			SET value = {0}
			WHERE id = {1}
		'''.format(value,id)

		try:
			self.CURS.execute(query)
			self.DB.commit()
		except:
			return -1
		
		return self.CURS.lastrowid
	
	def DeleteThreshold(self, id):
		self.CURS.execute('''
			DELETE FROM stocks_thresholds
			WHERE id = {0}
		'''.format(id))
		self.DB.commit()
	
	# ---- THRESHOLDS ----
	
	def GetStockHistoryActionById(self, act_id):
		query = "SELECT * FROM stocks_history WHERE id={0}".format(act_id)
		self.CURS.execute(query)
		
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return {
					"id": 		 	rows[0][0],
					"timestamp": 	rows[0][1],
					"date": 	 	rows[0][2],
					"ticker":		rows[0][3],
					"price": 	 	rows[0][4],
					"action": 	 	rows[0][5],
					"amount": 	 	rows[0][6],
					"fee": 			rows[0][7],
					"action_name": 	rows[0][5],
					"leftovers":	rows[0][8],
					"risk":			rows[0][9],
				}
		return None
	
	def GetStockHistorySellInfoByBuyId(self, act_id):
		print("GetStockHistorySellInfoByBuyId")
		query = '''
			SELECT * FROM stocks_history_sell_info
			WHERE stocks_history_buy_id = {0}
		'''.format(act_id)
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"id": 		 				row[0],
					"stocks_history_sell_id": 	row[1],
					"stocks_history_buy_id": 	row[2],
					"quantity": 	 			row[3]
				})
		return stocks
	
	def GetStockHistorySellInfoBySellId(self, act_id):
		print("GetStockHistorySellInfoBySellId")
		query = '''
			SELECT * FROM stocks_history_sell_info
			WHERE stocks_history_sell_id = {0}
		'''.format(act_id)
		self.CURS.execute(query)
		
		stocks = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				stocks.append({
					"id": 		 				row[0],
					"stocks_history_sell_id": 	row[1],
					"stocks_history_buy_id": 	row[2],
					"quantity": 	 			row[3]
				})
		return stocks
	
	def SelectYFInfo(self, ticker):
		query = '''
			SELECT yf_info FROM stocks_info
			WHERE ticker = '{0}'
		'''.format(ticker)
		self.CURS.execute(query)

		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return rows[0][0]
		return None
	
	def InsertStockToPortfolio(self, ticker, portfolio_id):
		query = '''
			INSERT INTO stock_to_portfolio (ticker,portfolio_id)
			VALUES ('{0}',{1})
		'''.format(ticker,portfolio_id)
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	# Dubble implementation
	def InsertStockPortfolio(self, data):
		query = '''
			INSERT INTO stock_to_portfolio (ticker,portfolio_id)
			VALUES ('{0}',{1})
		'''.format(data["ticker"],data["id"])

		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def InsertStockHistory(self, transaction):
		leftovers = 0
		if transaction["action"] == -1:
			leftovers = transaction["amount"]
		
		query = '''
			INSERT INTO stocks_history (id,timestamp,date,ticker,price,action,amount,fee,leftovers,risk)
			VALUES (NULL,{0},'{1}','{2}',{3},{4},{5},{6},{7},{8})
		'''.format(transaction["timestamp"],transaction["date"],transaction["ticker"],transaction["price"],transaction["action"],transaction["amount"],transaction["fee"],leftovers,transaction["risk"])

		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def InsertStockHistorySellInfo(self, transaction):	
		query = '''
			INSERT INTO stocks_history_sell_info (id,stocks_history_sell_id,stocks_history_buy_id,quantity)
			VALUES (NULL,{0},{1},{2})
		'''.format(transaction["stocks_history_sell_id"],transaction["stocks_history_buy_id"],transaction["quantity"])

		try:
			self.CURS.execute(query)
			self.DB.commit()
		except:
			return -1
		
		return self.CURS.lastrowid
	
	def InsertPortfolio(self, portfolio_name):
		query = '''
			INSERT INTO portfolios VALUES (NULL,'{0}')
		'''.format(portfolio_name)
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def UpdateYFInfo(self, ticker, info):
		query = '''
			UPDATE stocks_info
			SET yf_info = '{0}'
			WHERE ticker = '{1}'
		'''.format(info,ticker)

		try:
			self.CURS.execute(query)
			self.DB.commit()
		except:
			return -1
		
		return self.CURS.lastrowid
	
	def UpdateStockActionLeftoverById(self, act_id, leftover):
		query = '''
			UPDATE stocks_history
			SET leftovers = {0}
			WHERE id = {1}
		'''.format(leftover,act_id)

		try:
			self.CURS.execute(query)
			self.DB.commit()
		except:
			return -1
		
		return self.CURS.lastrowid
	
	def DeleteStockPortfolio(self, data):
		query = '''
			DELETE FROM stock_to_portfolio
			WHERE ticker = '{0}' AND portfolio_id = {1}
		'''.format(data["ticker"],data["id"])

		self.CURS.execute(query)
		self.DB.commit()
	
	def DeletePortfolio(self, id):
		self.CURS.execute('''
			DELETE FROM stock_to_portfolio
			WHERE portfolio_id = {0}
		'''.format(id))
		self.DB.commit()

		self.CURS.execute('''
			DELETE FROM portfolios
			WHERE id = {0}
		'''.format(id))
		self.DB.commit()
	
	def DeleteActionById(self, id):
		self.CURS.execute('''
			DELETE FROM stocks_history
			WHERE id = '{0}'
		'''.format(id))
		self.DB.commit()

	def DeleteStockHistorySellInfoByBuyId(self, item_id):
		print("DeleteStockHistorySellInfoByBuyId")
		query = '''
			DELETE FROM stocks_history_sell_info
			WHERE stocks_history_buy_id={0}
		'''.format(item_id)

		self.CURS.execute(query)
		self.DB.commit()
	
	def DeleteStockHistorySellInfoBySellId(self, item_id):
		query = '''
			DELETE FROM stocks_history_sell_info
			WHERE stocks_history_sell_id={0}
		'''.format(item_id)

		self.CURS.execute(query)
		self.DB.commit()