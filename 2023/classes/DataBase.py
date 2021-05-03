#!/usr/bin/python
import os
import sys
import time
import base64
import datetime
from datetime import date
from datetime import datetime
import _thread
import threading

import math
import sqlite3

class DB():
	def __init__(self, path):
		path = os.path.join("", path)
		self.ClassName		= "DB"
		self.DB 			= sqlite3.connect(path, check_same_thread=False)
		self.CURS			= self.DB.cursor()
		self.Locker		 	= threading.Lock()

		self.BuildSchema()
	
	def BuildSchema(self):
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "funds_info" (
							"id"				INTEGER PRIMARY KEY AUTOINCREMENT,
							"number"			INTEGER,
							"name"				TEXT NOT NULL,
							"mngr"				TEXT,
							"ivest_mngr"		TEXT,
							"d_change" 			REAL,
							"month_begin"		REAL,
							"y_change"			REAL,
							"year_begin"		REAL,
							"fee" 				REAL,
							"fund_size"			REAL,
							"last_updated"		TEXT,
							"mimic"				INTEGER,
							"json"				TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stocks" (
							"id"				INTEGER PRIMARY KEY AUTOINCREMENT,
							"ticker"			TEXT NOT NULL,
							"name"				TEXT NOT NULL,
							"type"				INTEGER
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "stock_to_fund" (
							"fund_id"			INTEGER,
							"stock_id" 			INTEGER,
							"number"			INTEGER,
							"ticker"			TEXT NOT NULL,
							"val"				REAL,
							"amount"			REAL,
							"perc" 				REAL
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "fund_history_changes" (
							"id"				INTEGER PRIMARY KEY AUTOINCREMENT,
							"number" 			INTEGER,
							"name" 				TEXT,
							"date" 				TEXT,
							"timestamp"			INTEGER,
							"change"			TEXT
						);''')

		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "portfolios" (
							"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
							"name"	TEXT
						);''')
		
		self.CURS.execute('''CREATE TABLE IF NOT EXISTS "fund_to_portfolio" (
							"fund_id"		INTEGER NOT NULL,
							"portfolio_id"	INTEGER NOT NULL
						);''')
		
		self.Init()

	def Init(self):
		pass

	def CleanDB(self):
		self.Locker.acquire()
		try:
			query = "DELETE FROM funds_info"
			self.CURS.execute(query)
			self.DB.commit()

			query = "DELETE FROM stocks"
			self.CURS.execute(query)
			self.DB.commit()

			query = "DELETE FROM stock_to_fund"
			self.CURS.execute(query)
			self.DB.commit()
		except:
			pass
		self.Locker.release()

	def IsFundInfoExist(self, number):
		try:
			info = self.SelectFundInfoByNumber(number)
		except:
			pass

		if info is None:
			return False, None
		return True, info
	
	def SelectFundInfoByNumber(self, number):
		self.Locker.acquire()
		info = None
		try:
			query = "SELECT id,number,name,mngr,ivest_mngr,d_change,month_begin,y_change,year_begin,fee,fund_size,last_updated,mimic FROM funds_info WHERE number = {0}".format(number)
			self.CURS.execute(query)

			rows = self.CURS.fetchall()
			if len(rows) > 0:
				info = { 
					"id": 			rows[0][0],
					"number": 		rows[0][1],
					"name": 		rows[0][2],
					"mngr": 		rows[0][3],
					"ivest_mngr": 	rows[0][4],
					"d_change": 	rows[0][5],
					"month_begin": 	rows[0][6],
					"y_change": 	rows[0][7],
					"year_begin": 	rows[0][8],
					"fee": 			rows[0][9],
					"fund_size": 	rows[0][10],
					"last_updated": rows[0][11],
					"mimic": 		rows[0][12]
				}
		except:
			pass

		self.Locker.release()
		return info
	
	def SelectFundHoldingsByNumber(self, number):
		self.Locker.acquire()
		try:
			query = '''
					SELECT stock_to_fund.ticker, stock_to_fund.val, stock_to_fund.amount, stock_to_fund.perc FROM funds_info 
					INNER JOIN stock_to_fund ON funds_info.id = stock_to_fund.fund_id
					WHERE funds_info.number = {0}
					'''.format(number)
			self.CURS.execute(query)

			holdings = []
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					holdings.append({ 
						"ticker":	row[0],
						"val": 		row[1],
						"amount":	row[2],
						"perc":		row[3]
					})
		except:
			pass
		self.Locker.release()
		
		return holdings

	def SelectFundsInfo(self):
		self.Locker.acquire()
		try:
			query = "SELECT id,number,name,mngr,ivest_mngr,d_change,month_begin,y_change,year_begin,fee,fund_size,last_updated,mimic FROM funds_info"
			self.CURS.execute(query)

			funds = []
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					funds.append({ 
						"id": 			row[0],
						"number": 		row[1],
						"name": 		row[2],
						"mngr": 		row[3],
						"ivest_mngr": 	row[4],
						"d_change": 	row[5],
						"month_begin": 	row[6],
						"y_change": 	row[7],
						"year_begin": 	row[8],
						"fee": 			row[9],
						"fund_size": 	row[10],
						"last_updated": row[11],
						"mimic": 		row[12]
					})
		except:
			pass
		self.Locker.release()
		
		return funds

	def InsertFundInfo(self, fund):
		self.Locker.acquire()
		try:
			query = '''
				INSERT INTO funds_info (id,number,name,mngr,ivest_mngr,d_change,month_begin,y_change,year_begin,fee,fund_size,last_updated,mimic,json)
				VALUES (NULL,{0},'{1}','{2}','{3}',{4},{5},{6},{7},{8},{9},'{10}',{11},'{12}')
			'''.format(fund["number"],fund["name"],fund["mngr"],fund["ivest_mngr"],fund["d_change"],fund["month_begin"],fund["y_change"],fund["year_begin"],fund["fee"],fund["fund_size"],fund["last_updated"],fund["mimic"],fund["json"])
			self.CURS.execute(query)
			self.DB.commit()
			self.Locker.release()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR {0}".format(e))
		self.Locker.release()
		return 0

	def UpdateFundInfo(self, info):
		self.Locker.acquire()
		try:
			query = '''
				UPDATE funds_info
				SET name = '{0}',
					mngr = '{1}',
					ivest_mngr = '{2}',
					d_change = {3},
					month_begin = {4},
					y_change = {5},
					year_begin = {6},
					fee = {7},
					fund_size = {8},
					last_updated = '{9}',
					mimic = {10}
				WHERE number = '{11}'
			'''.format(info["name"],info["mngr"],info["ivest_mngr"],info["d_change"],info["month_begin"],info["y_change"],info["year_begin"],info["fee"],info["fund_size"],info["last_updated"],info["mimic"],info["number"])

		
			self.CURS.execute(query)
			self.DB.commit()
		except:
			self.Locker.release()
			return -1
		
		self.Locker.release()
		return self.CURS.lastrowid

	def DeleteFundInfo(self, number):
		pass
	
	def IsStockExist(self, ticker):
		self.Locker.acquire()
		try:
			query = "SELECT id,ticker,name,type FROM stocks WHERE ticker = '{0}'".format(ticker)
			self.CURS.execute(query)

			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:				
				return True, { 
					"id": 		rows[0][0],
					"ticker": 	rows[0][1],
					"name": 	rows[0][2],
					"type": 	rows[0][3]
				}
		except Exception as e:
			print("ERROR [IsStockExist] {0}".format(e))
			self.Locker.release()
		
		return False, None
	
	def InsertStock(self, stock):
		self.Locker.acquire()
		try:
			query = '''
				INSERT INTO stocks (id,ticker,name,type)
				VALUES (NULL,'{0}','{1}',{2})
			'''.format(stock["ticker"],stock["name"],stock["type"])
			self.CURS.execute(query)
			self.DB.commit()
			self.Locker.release()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR [InsertStock] {0}".format(e))
			self.Locker.release()
		
		return 0
	
	def IsFundToStockExist(self, fund_id, stock_id):
		self.Locker.acquire()
		try:
			query = "SELECT * FROM stock_to_fund WHERE fund_id = {0} AND stock_id = {1}".format(fund_id, stock_id)
			self.CURS.execute(query)
			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:
				return True
		except Exception as e:
			print("ERROR [IsFundToStockExist] {0}".format(e))
			self.Locker.release()

		return False
	
	def InsertStockToFund(self, bond):
		self.Locker.acquire()
		try:
			query = '''
				INSERT INTO stock_to_fund (fund_id,stock_id,number,ticker,val,amount,perc)
				VALUES ({0},{1},{2},'{3}',{4},{5},{6})
			'''.format(bond["fund_id"],bond["stock_id"],bond["number"],bond["ticker"],bond["val"],bond["amount"],bond["perc"])
			self.CURS.execute(query)
			self.DB.commit()
			self.Locker.release()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR [InsertStockToFund] {0}".format(e))
			self.Locker.release()
		
		return 0
	
	def InsertFundHistoryChange(self, item):
		self.Locker.acquire()
		try:
			now = datetime.now()
			date_str = now.strftime("%m-%d-%Y 00:00:00")

			query = '''
				INSERT INTO fund_history_changes (id,number,name,date,timestamp,change)
				VALUES (NULL, {0},'{1}','{2}',{3},'{4}')
			'''.format(item["number"],item["name"],date_str,time.time(),item["msg"])
			self.CURS.execute(query)
			self.DB.commit()
			self.Locker.release()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR [InsertFundHistoryChange] {0}\n{1}".format(e,query))
		
		self.Locker.release()
		return 0

	def SelectStocksRate(self):
		self.Locker.acquire()
		try:
			query = '''
				SELECT stocks.name, stocks.ticker, stocks.type, count(stocks.ticker) as funds_count FROM stocks
				LEFT JOIN stock_to_fund ON stocks.id = stock_to_fund.stock_id
				GROUP BY stocks.ticker
				ORDER BY funds_count DESC
			'''
			self.CURS.execute(query)

			funds = []
			rows = self.CURS.fetchall()
			if len(rows) > 0:
				for row in rows:
					funds.append({ 
						"name": 		row[0],
						"ticker": 		row[1],
						"type": 		row[2],
						"funds_count": 	row[3],
					})
		except:
			pass
		self.Locker.release()
		
		return funds
	
	def GetPortfolios(self):
		self.Locker.acquire()
		try:
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
		except Exception as e:
			print("ERROR [GetPortfolios] {0}".format(e))
		
		self.Locker.release()
		return portfolios
	
	def PortfolioExist(self, portfolio_name):
		self.Locker.acquire()
		try:
			query = "SELECT * FROM portfolios WHERE name = '{0}'".format(portfolio_name)
			self.CURS.execute(query)
			
			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:
				return True
		except Exception as e:
			print("ERROR [PortfolioExist] {0}".format(e))
			self.Locker.release()
		
		return False
	
	def InsertPortfolio(self, portfolio_name):
		self.Locker.acquire()
		try:
			query = '''
				INSERT INTO portfolios VALUES (NULL,'{0}')
			'''.format(portfolio_name)
			self.CURS.execute(query)
			self.DB.commit()
		except Exception as e:
			print("ERROR [InsertPortfolio] {0}".format(e))
		
		self.Locker.release()	
		return self.CURS.lastrowid
	
	def InsertFundPortfolio(self, data):
		self.Locker.acquire()
		try:
			query = '''
				INSERT INTO fund_to_portfolio (fund_id,portfolio_id)
				VALUES ('{0}',{1})
			'''.format(data["fund_id"],data["portfolio_id"])

			self.CURS.execute(query)
			self.DB.commit()
		except Exception as e:
			print("ERROR [InsertFundPortfolio] {0}".format(e))
		
		self.Locker.release()	
		return self.CURS.lastrowid
	
	def DeleteFundPortfolio(self, data):
		self.Locker.acquire()
		try:
			query = '''
				DELETE FROM fund_to_portfolio
				WHERE fund_id = '{0}' AND portfolio_id = {1}
			'''.format(data["fund_id"],data["id"])

			self.CURS.execute(query)
			self.DB.commit()
		except Exception as e:
			print("ERROR [DeleteFundPortfolio] {0}".format(e))
		
		self.Locker.release()	
	
	def DeletePortfolio(self, id):
		self.Locker.acquire()
		try:
			self.CURS.execute('''
				DELETE FROM fund_to_portfolio
				WHERE portfolio_id = {0}
			'''.format(id))
			self.DB.commit()

			self.CURS.execute('''
				DELETE FROM portfolios
				WHERE id = {0}
			'''.format(id))
			self.DB.commit()
		except Exception as e:
			print("ERROR [DeletePortfolio] {0}".format(e))
		
		self.Locker.release()	
	
	def HowManyStocksWeHave(self):
		self.Locker.acquire()
		try:
			query = "SELECT COUNT(*) FROM stocks"
			self.CURS.execute(query)
			
			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:
				return rows[0][0]
		except Exception as e:
			print("ERROR [PortfolioExist] {0}".format(e))
		
		self.Locker.release()
		return 0
	
	def HowManyStocksFundHas(self, numbers):
		self.Locker.acquire()
		try:
			query = '''
				SELECT COUNT(*) FROM (
				SELECT stocks.ticker, stocks.name, stocks.type, count(stocks.ticker) as rate FROM stocks
				LEFT JOIN stock_to_fund ON stocks.id = stock_to_fund.stock_id
				WHERE stock_to_fund.number IN ({0})
				GROUP BY stocks.ticker )
			'''.format(numbers)
			self.CURS.execute(query)
			
			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:
				return rows[0][0]
		except Exception as e:
			print("ERROR [PortfolioExist] {0}".format(e))
			self.Locker.release()
		
		return 0

	def GetStocksDistribution(self, numbers, stock_type):
		self.Locker.acquire()
		try:
			query = '''
				SELECT COUNT(*) FROM (
				SELECT stocks.ticker, stocks.name, stocks.type, count(stocks.ticker) as rate FROM stocks
				LEFT JOIN stock_to_fund ON stocks.id = stock_to_fund.stock_id
				WHERE stocks.type = {1} AND stock_to_fund.number IN ({0})
				GROUP BY stocks.ticker )
			'''.format(numbers, stock_type)
			self.CURS.execute(query)
			
			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:
				return rows[0][0]
		except Exception as e:
			print("ERROR [PortfolioExist] {0}".format(e))
			self.Locker.release()
		
		return 0
	
	def GetStocksInvestement(self, numbers):
		data = []
		self.Locker.acquire()
		try:
			query = '''
				SELECT
					funds_info.number,
					COUNT(stocks.id) AS holdings_count,
					count(case when stocks.type = 1 then 1 end) type_1,
					count(case when stocks.type = 3 then 1 end) type_3,
					count(case when stocks.type = 5 then 1 end) type_5,
					count(case when stocks.type = 6 then 1 end) type_6,
					count(case when stocks.type = 7 then 1 end) type_7,
					count(case when stocks.type = 9 then 1 end) type_9,
					count(case when stocks.type = 10 then 1 end) type_10,
					count(case when stocks.type = 11 then 1 end) type_11,
					count(case when stocks.type = 12 then 1 end) type_12,
					count(case when stocks.type = 13 then 1 end) type_13,
					count(case when stocks.type = 14 then 1 end) type_14,
					count(case when stocks.type = 15 then 1 end) type_15,
					count(case when stocks.type = 17 then 1 end) type_17,
					count(case when stocks.type = 18 then 1 end) type_18,
					count(case when stocks.type = 19 then 1 end) type_19,
					count(case when stocks.type = 22 then 1 end) type_22,
					count(case when stocks.type = 33 then 1 end) type_33,
					count(case when stocks.type = 34 then 1 end) type_34,
					count(case when stocks.type = 35 then 1 end) type_35,
					count(case when stocks.type = 36 then 1 end) type_36,
					count(case when stocks.type = 43 then 1 end) type_43,
					count(case when stocks.type = 44 then 1 end) type_44,
					count(case when stocks.type = 45 then 1 end) type_45,
					count(case when stocks.type = 50 then 1 end) type_50,
					count(case when stocks.type = 51 then 1 end) type_51,
					count(case when stocks.type = 100 then 1 end) type_100,
					count(case when stocks.type = 102 then 1 end) type_102,
					count(case when stocks.type = 1001 then 1 end) type_1001
				FROM funds_info
				LEFT JOIN stock_to_fund ON funds_info.id = stock_to_fund.fund_id
				LEFT JOIN stocks ON stock_to_fund.stock_id = stocks.id
				WHERE funds_info.number IN ({0})
				GROUP BY funds_info.number
			'''.format(numbers)
			self.CURS.execute(query)
			
			rows = self.CURS.fetchall()
			self.Locker.release()
			if len(rows) > 0:
				for row in rows:
					data.append({
						"number": row[0],
						"holdings_count": row[1],
						"is_holdings": row[2],
						"us_holdings": row[29],
						"other_holdings": row[1] - (row[2] + row[29])
					})
		except Exception as e:
			print("ERROR [PortfolioExist] {0}".format(e))
			self.Locker.release()
		
		return data

'''
SELECT * FROM (
SELECT stocks.name, stocks.ticker, stocks.type, count(stocks.ticker) as funds_count FROM stocks
LEFT JOIN stock_to_fund ON stocks.id = stock_to_fund.stock_id
GROUP BY stocks.ticker
ORDER BY funds_count DESC)
WHERE ticker == "DIS"

1 - MENAYOT
3 - יהש
5
6
7
9
10 - AGAH
11
12 - MIMSHALTI
13 - MAKAM
14
15
17
18
19 - TREASURY
22 - AGAH
33 - MADADIM
34
35
36 - CURRENCY
(*) 43 - TRUST
44 - ETFS
45
50 - HTF
51 - SAL
100 - (?)
102 - NAAM
(*) 1001 - STOCKS

'''