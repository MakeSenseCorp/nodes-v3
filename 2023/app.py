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

from mksdk import MkSFile
from mksdk import MkSSlaveNode
from mksdk import MkSScheduling
from mksdk import MkSFileUploader

from classes import FunderAPI
from classes import DataBase

class Context():
	def __init__(self, node):
		self.ClassName					= "Apllication"
		self.Timer						= MkSScheduling.TimeSchedulerThreadless()
		self.Node						= node
		self.File						= MkSFile.File()
		self.Funder 					= FunderAPI.Funder(self.Node)
		self.SQL 						= DataBase.DB("funder.db")
		# States
		self.States = {
		}
		# Handlers
		self.Node.ApplicationRequestHandlers	= {
			'get_sensor_info':					self.GetSensorInfoHandler,
			'confuguration': 					self.ConfigurationHandler,
			'get_all_funds': 					self.GetAllFundsHandler,
			'get_fund_info': 					self.GetFundInfoHandler,
			'get_stocks_rate':					self.GetStocksRateHandler,
			'get_portfolios':					self.GetPortfoliosHandler,
			'create_new_portfolio':				self.CreateNewPortfolioHandler,
			'delete_portfolio':					self.DeletePortfolioHandler,
			'get_stock_investment':				self.GetStockInvestmentHandler,
			'undefined':						self.UndefindHandler
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
		self.DBUpdateStatus 			= {
			"status": "IDLE",
			"update_perc": 0,
			"working": False
		}
	
	def UndefindHandler(self, sock, packet):
		print ("UndefindHandler")
	
	def GetStockInvestmentHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetStockInvestmentHandler]".format(classname=self.ClassName),5)

		funds_number_list = payload["funds"]
		str_numbers = ",".join([str(num) for num in funds_number_list])

		all_stocks = self.SQL.HowManyStocksFundHas(str_numbers)
		us_stocks = self.SQL.GetStocksInvestement(str_numbers, 1001)
		is_stocks = self.SQL.GetStocksInvestement(str_numbers, 1)
		government_stocks = all_stocks - (us_stocks + is_stocks)

		data = {
			"us": us_stocks,
			"is": is_stocks,
			"government": government_stocks,
			"all": all_stocks
		}
		self.Node.LogMSG("({classname})# [GetStockInvestmentHandler] {0}".format(data, classname=self.ClassName),5)

		return data

	def GetPortfoliosHandler(self, sock, packet):
		self.Node.LogMSG("({classname})# [GetPortfoliosHandler]".format(classname=self.ClassName),5)
		
		return {
			"portfolios": self.SQL.GetPortfolios()
		}
	
	def CreateNewPortfolioHandler(self, sock, packet):
		payload	= self.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [CreateNewPortfolioHandler]".format(classname=self.ClassName),5)
		res = self.SQL.InsertPortfolio(payload["name"])

		return {
			"id": res
		}
	
	def DeletePortfolioHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [DeletePortfolioHandler] {0}".format(payload,classname=self.ClassName),5)
		self.SQL.DeletePortfolio(payload["id"])
		return {
			"portfolios": self.SQL.GetPortfolios()
		}

	def GetStocksRateHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetStocksRateHandler] {0}".format(payload,classname=self.ClassName),5)

		return {
			"ratings": self.SQL.SelectStocksRate()
		}

	def GetFundInfoHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [GetFundInfoHandler] {0}".format(payload,classname=self.ClassName),5)

		number = payload["number"]
		return {
			"holdings": self.SQL.SelectFundHoldingsByNumber(number)
		}

	def GetAllFundsHandler(self, sock, packet):
		self.Node.LogMSG("({classname})# [GetAllFundsHandler]".format(classname=self.ClassName),5)

		return {
			"funds": self.SQL.SelectFundsInfo()
		}

	def ConfigurationHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [ConfigurationHandler] {0}".format(payload,classname=self.ClassName),5)
		operation = payload["operation"]

		if "clean" in operation:
			self.SQL.CleanDB()
		elif "update_start" in operation:
			self.UpdateFundsInfo()
			return {
				"status": True
			}
		elif "update_stop" in operation:
			self.DBUpdateStatus["working"] = False
			return {
				"status": True
			}
		elif "status" in operation:
			return {
				"update_status": self.DBUpdateStatus
			}
		else:
			pass
		
		return {
			"error": "none"
		}
	
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

	def CheckForFundInfoChange(self, left, right):
		msg = ""
		if left["number"] != right["number"]:
			return False
		if left["name"] != right["name"]:
			msg += "Name {0} -> {1}\n".format(left["name"],right["name"])
		if left["mngr"] != right["mngr"]:
			msg += "Manager {0} -> {1}\n".format(left["mngr"],right["mngr"])
		if left["ivest_mngr"] != right["ivest_mngr"]:
			msg += "Investing Manager {0} -> {1}\n".format(left["ivest_mngr"],ivest_mngr["name"])
		if left["d_change"] != right["d_change"]:
			msg += "Day Change {0} -> {1}\n".format(left["d_change"],right["d_change"])
		if left["month_begin"] != right["month_begin"]:
			msg += "Monthly Change {0} -> {1}\n".format(left["month_begin"],right["month_begin"])
		if left["y_change"] != right["y_change"]:
			msg += "Year Change {0} -> {1}\n".format(left["y_change"],right["y_change"])
		if left["year_begin"] != right["year_begin"]:
			msg += "Yearly Change {0} -> {1}\n".format(left["year_begin"],right["year_begin"])
		if left["fee"] != right["fee"]:
			msg += "Fee {0} -> {1}\n".format(left["fee"],right["fee"])
		if left["fund_size"] != right["fund_size"]:
			msg += "Fund Size {0} -> {1}\n".format(left["fund_size"],right["fund_size"])
		if left["last_updated"] != right["last_updated"]:
			msg += "Last Update {0} -> {1}\n".format(left["last_updated"],right["last_updated"])
		if left["mimic"] != right["mimic"]:
			msg += "Mimic Fund {0} -> {1}\n".format(left["mimic"],right["mimic"])
	
		self.SQL.InsertFundHistoryChange({
						"number": right["number"],
						"name": right["name"],
						"msg": msg
					})
		return True

	def CheckValidity(self, fund):
		if fund["number"] is None:
			return False, None
		
		if fund["name"] is None:
			fund["name"] = ""
		if fund["mngr"] is None:
			fund["mngr"] = ""
		if fund["ivest_mngr"] is None:
			fund["ivest_mngr"] = ""
		if fund["d_change"] is None:
			fund["d_change"] = 0.0
		if fund["month_begin"] is None:
			fund["month_begin"] = 0.0
		if fund["y_change"] is None:
			fund["y_change"] = 0.0
		if fund["year_begin"] is None:
			fund["year_begin"] = 0.0
		if fund["fee"] is None:
			fund["fee"] = 0.0
		if fund["fund_size"] is None:
			fund["fund_size"] = 0.0
		if fund["last_updated"] is None:
			fund["last_updated"] = ""
		if fund["mimic"] is None:
			fund["mimic"] = ""
		
		return True, fund
	
	def FindDifference(self, old, new):
		new_items 		= []
		deleted_items 	= []
		for item in old:
			if item not in new:
				deleted_items.append(item)
		for item in new:
			if item not in old:
				new_items.append(item)
		
		return new_items, deleted_items
	
	def GenerateTickerListFromFunder(self, info):
		tickers = []
		for holds in info:
			holding_list = holds["holdingItemsList"]
			for hold in holding_list:
				if hold["TICKER"] != "":
					tickers.append(hold["TICKER"])
		return tickers
	
	def GenerateTickerListFromDB(self, number):
		tickers = []
		stocks = self.SQL.SelectFundHoldingsByNumber(number)
		for stock in stocks:
			if stock["ticker"] != "":
				tickers.append(stock["ticker"])
		return tickers

	def UpdateFundHoldings(self, fund):
		self.Node.LogMSG("({classname})# Request fund's holdings".format(classname=self.ClassName),5)
		# Get fund info
		info = self.Funder.GetFundInfoFromDB(fund["fundNum"])
		if info is not None:
			# TODO - Check for stock list difference
			new_ticker_list = self.GenerateTickerListFromFunder(info["holdings"])
			old_ticker_list = self.GenerateTickerListFromDB(fund["fundNum"])
			new, deleted = self.FindDifference(old_ticker_list, new_ticker_list)

			if len(new) > 0:
				for item in new:
					self.SQL.InsertFundHistoryChange({
						"number": fund["fundNum"],
						"name": fund["fundName"],
						"msg": "New stock ({0}) was added to {1} {2}".format(item,fund["fundNum"],fund["fundName"])
					})
			
			if len(deleted) > 0:
				for item in deleted:
					self.SQL.InsertFundHistoryChange({
						"number": fund["fundNum"],
						"name": fund["fundName"],
						"msg": "Stock ({0}) was deleted from {1} ({2})".format(item,fund["fundNum"],fund["fundName"])
					})
					# Delete from stock_to_fund

			for holds in info["holdings"]:
				holding_list = holds["holdingItemsList"]
				for hold in holding_list:
					if hold["TICKER"] != "":
						stock_db = {
							"name": 	hold["aName"],
							"ticker": 	hold["TICKER"],
							"type": 	hold["fType"]
						}
						bond_db = {
							"number": 	fund["fundNum"],
							"ticker": 	hold["TICKER"],
							"perc": 	hold["perc"],
							"val": 		hold["valShk"],
							"amount": 	hold["amount"]
						}

						stock_id = 0
						fund_id  = fund["fund_id"]
						is_exist, item = self.SQL.IsStockExist(hold["TICKER"])
						if is_exist is False:
							self.Node.LogMSG("({classname})# Update local DB with holding ({0}) ".format(hold["TICKER"],classname=self.ClassName),5)
							stock_id = self.SQL.InsertStock(stock_db)
						else:
							stock_id = item["id"]
						
						# Check if this constalation exist
						if self.SQL.IsFundToStockExist(fund_id, stock_id) is False:
							bond_db["fund_id"]  = fund_id
							bond_db["stock_id"] = stock_id
							self.Node.LogMSG("({classname})# Update local DB with bonding ({0}) {1} ({2} -> {3})".format(fund["fundNum"], hold["TICKER"],fund_id,stock_id,classname=self.ClassName),5)
							self.SQL.InsertStockToFund(bond_db)
						else:
							pass

	def DBUpdateWorker(self):
		self.Node.LogMSG("({classname})# Request all funds from Funnder".format(classname=self.ClassName),5)
		funds = self.Funder.GetFunderJsonDB()
		if funds is not None:
			funds_count = len(funds)
			for idx, fund in enumerate(funds[:]):
				try:
					# Exit on request
					if self.DBUpdateStatus["working"] is False:
						break
					# 5108428 - ERROR (GetFundInfoFromDB): Fund id 5108428 ('str' object has no attribute 'decode')
					self.DBUpdateStatus["status"] = "UPDATE"
					self.DBUpdateStatus["update_perc"] = (float(idx) / float(funds_count)) * 100.0
					number = fund["fundNum"]
					fund_db = {
						"number": 		number,
						"name":			fund["fundName"],
						"mngr":			fund["fundMng"],
						"ivest_mngr":	fund["invstMng"],
						"d_change":		fund["1day"],
						"month_begin":	fund["monthBegin"],
						"y_change":		fund["1year"],
						"year_begin":	fund["yearBegin"],
						"fee":			fund["nihol"],
						"fund_size":	fund["rSize"],
						"last_updated":	fund["lastUpdate"],
						"mimic":		fund["mehaka"],
						"json":			"" # json.dumps(fund,ensure_ascii=False)
					}
					if fund is not None:
						valid, data = self.CheckValidity(fund_db)
						if valid is True:
							is_exist, item = self.SQL.IsFundInfoExist(number)
							if is_exist is False:
								self.Node.LogMSG("({classname})# Insert local DB with fund ({0}) info ".format(number,classname=self.ClassName),5)
								fund["fund_id"] = self.SQL.InsertFundInfo(data)
								self.UpdateFundHoldings(fund)
							else:
								if fund["lastUpdate"] not in item["last_updated"]:
									self.Node.LogMSG("({classname})# Update local DB with fund ({0}) info ".format(number,classname=self.ClassName),5)
									# TODO - Check for info changes
									info = self.SQL.SelectFundInfoByNumber(number)
									# self.CheckForFundInfoChange(info, fund_db)
									self.SQL.UpdateFundInfo(data)
									fund["fund_id"] = item["id"]
									self.UpdateFundHoldings(fund)
								else:
									pass
				except Exception as e:
					print("ERROR (DBUpdateWorker): Fund id {0} ({1})".format(number,e))
		
		self.DBUpdateStatus["working"] 		= False
		self.DBUpdateStatus["status"] 		= "IDLE"
		self.DBUpdateStatus["update_perc"] 	= 0
	
	def UpdateFundsInfo(self):
		self.DBUpdateStatus["working"] = True
		_thread.start_new_thread(self.DBUpdateWorker, ())

	def NodeSystemLoadedHandler(self):
		self.Node.LogMSG("({classname})# Loading system ...".format(classname=self.ClassName),5)
		# Get all funds from Funder
		self.Node.LogMSG("({classname})# Loading system ... Done.".format(classname=self.ClassName),5)
	
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
