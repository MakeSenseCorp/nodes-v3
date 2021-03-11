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
							"market_price"	REAL
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
					"name": row[0],
					"ticker": row[1],
					"sector": row[2],
					"industry": row[3],
					"market_price": row[4]
				})
		return stocks
	
	def GetTickers(self):
		query = "SELECT * FROM stocks_info"
		self.CURS.execute(query)
		
		tickers = []
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			for row in rows:
				tickers.append(row[1])
		return tickers

	def GetStockExtetendedInfo(self, ticker):
		query = '''
		SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, hist_max, hist_min FROM stocks_info 
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
					"ticker": rows[0][0],
					"name": rows[0][1],
					"market_price": rows[0][2],
					"curr_price_sum": rows[0][3],
					"hist_price_sum": rows[0][4],
					"amount_sum": rows[0][5],
					"hist_max": rows[0][6],
					"hist_min": rows[0][7]
				}
		return None

	def GetPortfolioStocks(self, id):
		stocks = []
		if 0 == id:
			query = '''
			SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, stock_to_portfolio.portfolio_id, hist_max, hist_min FROM stocks_info 
			LEFT JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			LEFT JOIN (
				SELECT ticker, ABS(SUM(price * action * amount)) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
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
			SELECT stocks_info.ticker, name, stocks_info.market_price, ABS(market_price * amount_sum) as curr_price_sum, hist_price_sum, amount_sum, stock_to_portfolio.portfolio_id, hist_max, hist_min FROM stocks_info 
			LEFT JOIN stock_to_portfolio ON stocks_info.ticker == stock_to_portfolio.ticker
			LEFT JOIN (
				SELECT ticker, ABS(SUM(price * action * amount)) as hist_price_sum, ABS(SUM(action * amount)) as amount_sum
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
					"ticker": row[0],
					"name": row[1],
					"market_price": row[2],
					"curr_price_sum": row[3],
					"hist_price_sum": row[4],
					"amount_sum": row[5],
					"portfolio_id": row[6],
					"hist_max": row[7],
					"hist_min": row[8]
				})
		return stocks
	
	def GetStockHistory(self, ticker):
		query = '''
			SELECT timestamp, date, price, amount, name, action, fee FROM stocks_history
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
					"action_name": row[4],
					"fee": row[6]
				})
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
	
	def StockExist(self, ticker):
		if self.GetStock(ticker) is not None:
			return True
		return False
	
	def GetStock(self, ticker):
		query = "SELECT * FROM stocks_info WHERE ticker='{0}'".format(ticker)
		self.CURS.execute(query)
		
		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return rows[0]
		return None
	
	def InsertStock(self, stock):
		query = '''
			INSERT INTO stocks_info (id,name,ticker,sector,industry,market_price)
			VALUES (NULL,'{0}','{1}','{2}','{3}',{4})
		'''.format(stock["name"],stock["ticker"].upper(),stock["sector"],stock["industry"],stock["market_price"])
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def InsertStockToPortfolio(self, ticker, portfolio_id):
		query = '''
			INSERT INTO stock_to_portfolio (ticker,portfolio_id)
			VALUES ('{0}',{1})
		'''.format(ticker,portfolio_id)
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def InsertStockHistory(self, transaction):
		query = '''
			INSERT INTO stocks_history (id,timestamp,date,ticker,price,action,amount,fee,leftovers,risk)
			VALUES (NULL,{0},'{1}','{2}',{3},{4},{5},{6},{7},{8})
		'''.format(transaction["timestamp"],transaction["date"],transaction["ticker"],transaction["price"],transaction["action"],transaction["amount"],transaction["fee"],0,2.0)

		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def InsertPortfolio(self, portfolio_name):
		query = '''
			INSERT INTO portfolios VALUES (NULL,'{0}')
		'''.format(portfolio_name)
		self.CURS.execute(query)
		self.DB.commit()
		return self.CURS.lastrowid
	
	def InsertStockPortfolio(self, data):
		query = '''
			INSERT INTO stock_to_portfolio (ticker,portfolio_id)
			VALUES ('{0}',{1})
		'''.format(data["ticker"],data["id"])

		self.CURS.execute(query)
		self.DB.commit()
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
