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
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_info" (
							"id"			INTEGER PRIMARY KEY AUTOINCREMENT,
							"created_date" 	TEXT NOT NULL,
							"name"			TEXT NOT NULL,
							"ticker"		TEXT NOT NULL,
							"sector"		TEXT,
							"industry"		TEXT,
							"market_price"	REAL,
							"json_info"		TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks_price_history" (
							"id"			INTEGER PRIMARY KEY AUTOINCREMENT,
							"timestamp"		REAL NOT NULL,
							"date"			TEXT NOT NULL,
							"ticker"		TEXT NOT NULL,
							"open"			REAL NOT NULL,
							"close"			REAL NOT NULL,
							"high"			REAL NOT NULL,
							"low"			REAL NOT NULL,
							"vol"			REAL NOT NULL
						);''')

		self.Init()

	def Init(self):
		self.DB.commit()
	
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
					"json_info":	row[6]
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
	
	def GetStockHistory(self, period):
		query = "SELECT * FROM stocks_price_history".format(act_id)
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
	
	def InsertStock(self, stock):
		query = '''
			INSERT INTO stocks_info (id,name,ticker,sector,industry,market_price,yf_info)
			VALUES (NULL,'{0}','{1}','{2}','{3}',{4},'')
		'''.format(stock["name"],stock["ticker"].upper(),stock["sector"],stock["industry"],stock["market_price"])
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

		self.CURS.execute('''
			DELETE FROM stocks_info
			WHERE ticker = '{0}'
		'''.format(ticker))
		self.DB.commit()
	
	def DeleteActionById(self, id):
		self.CURS.execute('''
			DELETE FROM stocks_history
			WHERE id = '{0}'
		'''.format(id))
		self.DB.commit()
