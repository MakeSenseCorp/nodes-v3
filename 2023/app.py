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
	
	def UndefindHandler(self, sock, packet):
		print ("UndefindHandler")
	
	def ConfigurationHandler(self, sock, packet):
		payload = THIS.Node.BasicProtocol.GetPayloadFromJson(packet)
		self.Node.LogMSG("({classname})# [ConfigurationHandler] {0}".format(payload,classname=self.ClassName),5)
		operation = payload["operation"]

		if "clean" in operation:
			self.SQL.CleanDB()
		elif "update" in operation:
			pass
		else:
			pass
		
		return {

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

	def NodeSystemLoadedHandler(self):
		self.Node.LogMSG("({classname})# Loading system ...".format(classname=self.ClassName),5)
		# Get all funds from Funder
		self.Node.LogMSG("({classname})# Request all funds from Funnder".format(classname=self.ClassName),5)
		funds = self.Funder.GetFunderJsonDB()
		if funds is not None:
			for fund in funds[:10]:
				fund_db = {
					"number": 		fund["fundNum"],
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
				valid, data = self.CheckValidity(fund_db)
				if valid is True:
					self.Node.LogMSG("({classname})# Update local DB with fund ({0}) info ".format(fund["fundNum"],classname=self.ClassName),5)
					if self.SQL.IsFundInfoExist(fund["fundNum"]) is False:
						self.SQL.InsertFundInfo(data)
					else:
						self.SQL.UpdateFundInfo(data)
					
					self.Node.LogMSG("({classname})# Request fund's holdings".format(classname=self.ClassName),5)
					# Get fund info
					info = self.Funder.GetFundInfoFromDB(fund["fundNum"])
					if info is not None:
						for holds in info:
							holding_list = holds["holdingItemsList"]
							for hold in holding_list:
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
								self.Node.LogMSG("({classname})# Update local DB with holding ({0}) ".format(hold["TICKER"],classname=self.ClassName),5)
								if self.SQL.IsStockExist(hold["TICKER"]) is False:
									self.SQL.InsertStock(stock_db)
									self.SQL.InsertStockToFund(bond_db)
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
