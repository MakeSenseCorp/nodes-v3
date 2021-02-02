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
