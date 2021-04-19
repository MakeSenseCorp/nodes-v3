#!/usr/bin/python
import os
import sys
import time
import base64
import datetime
from datetime import date

import math
import sqlite3

class DB():
	def __init__(self, path):
		path = os.path.join("", path)
		self.ClassName	= "DB"
		self.DB 		= sqlite3.connect(path, check_same_thread=False)
		self.CURS		= self.DB.cursor()

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
							"change"			TEXT
						);''')

		self.Init()

	def Init(self):
		pass

	def CleanDB(self):
		query = "DELETE FROM funds_info"
		self.CURS.execute(query)
		self.DB.commit()

		query = "DELETE FROM stocks"
		self.CURS.execute(query)
		self.DB.commit()

		query = "DELETE FROM stock_to_fund"
		self.CURS.execute(query)
		self.DB.commit()

	def IsFundInfoExist(self, number):
		query = "SELECT id,number,name,mngr,ivest_mngr,d_change,month_begin,y_change,year_begin,fee,fund_size,last_updated,mimic FROM funds_info WHERE number = {0}".format(number)
		self.CURS.execute(query)

		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return True, { 
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
		
		return False, None

	def SelectFundsInfo(self):
		pass

	def InsertFundInfo(self, fund):
		try:
			query = '''
				INSERT INTO funds_info (id,number,name,mngr,ivest_mngr,d_change,month_begin,y_change,year_begin,fee,fund_size,last_updated,mimic,json)
				VALUES (NULL,{0},'{1}','{2}','{3}',{4},{5},{6},{7},{8},{9},'{10}',{11},'{12}')
			'''.format(fund["number"],fund["name"],fund["mngr"],fund["ivest_mngr"],fund["d_change"],fund["month_begin"],fund["y_change"],fund["year_begin"],fund["fee"],fund["fund_size"],fund["last_updated"],fund["mimic"],fund["json"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR {0}".format(e))
		return 0

	def UpdateFundInfo(self, number):
		pass

	def DeleteFundInfo(self, number):
		pass
	
	def IsStockExist(self, ticker):
		query = "SELECT id,ticker,name,type FROM stocks WHERE ticker = '{0}'".format(ticker)
		self.CURS.execute(query)

		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return True, { 
				"id": 		rows[0][0],
				"ticker": 	rows[0][1],
				"name": 	rows[0][2],
				"type": 	rows[0][3]
			}
		
		return False, None
	
	def InsertStock(self, stock):
		try:
			query = '''
				INSERT INTO stocks (id,ticker,name,type)
				VALUES (NULL,'{0}','{1}',{2})
			'''.format(stock["ticker"],stock["name"],stock["type"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR {0}".format(e))
		return 0
	
	def IsFundToStockExist(self, fund_id, stock_id):
		query = "SELECT * FROM stock_to_fund WHERE fund_id = {0} AND stock_id = {1}".format(fund_id, stock_id)
		self.CURS.execute(query)

		rows = self.CURS.fetchall()
		if len(rows) > 0:
			return True
		
		return False
	
	def InsertStockToFund(self, bond):
		try:
			query = '''
				INSERT INTO stock_to_fund (fund_id,stock_id,number,ticker,val,amount,perc)
				VALUES ({0},{1},{2},'{3}',{4},{5},{6})
			'''.format(bond["fund_id"],bond["stock_id"],bond["number"],bond["ticker"],bond["val"],bond["amount"],bond["perc"])
			self.CURS.execute(query)
			self.DB.commit()
			return self.CURS.lastrowid
		except Exception as e:
			print("ERROR {0}".format(e))
		return 0
