import json
import re
import time
import _thread
from collections import OrderedDict
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

from classes import definitions
from classes import webserver
from classes import sensordb
from classes import translator
from classes import common

class WebsocketLayer():
	def __init__(self):
		self.ClassName				= "WebsocketLayer"
		self.ApplicationSockets		= {}
		self.ServerRunning			= False
		# Events
		self.OnWSConnected			= None
		self.OnDataArrivedEvent		= None
		self.OnWSDisconnected		= None
		self.OnSessionsEmpty		= None
		self.Port					= 0
	
	def RegisterCallbacks(self, connected, data, disconnect, empty):
		print ("({classname})# (RegisterCallbacks)".format(classname=self.ClassName))
		self.OnWSConnected		= connected
		self.OnDataArrivedEvent = data
		self.OnWSDisconnected	= disconnect
		self.OnSessionsEmpty	= empty

	def SetPort(self, port):
		self.Port = port
	
	def AppendSocket(self, ws_id, ws):
		print ("({classname})# Append ({0})".format(ws_id, classname=self.ClassName))
		self.ApplicationSockets[ws_id] = ws
		if self.OnWSConnected is not None:
			self.OnWSConnected(ws_id)
	
	def RemoveSocket(self, ws_id):
		print ("({classname})# Remove ({0})".format(ws_id, classname=self.ClassName))
		del self.ApplicationSockets[ws_id]
		if self.OnWSDisconnected is not None:
			self.OnWSDisconnected(ws_id)
		if len(self.ApplicationSockets) == 0:
			if self.OnSessionsEmpty is not None:
				self.OnSessionsEmpty()
	
	def WSDataArrived(self, ws, data):
		packet = json.loads(data)
		print ("({classname})# Data {0}".format(id(ws),classname=self.ClassName))
		if self.OnDataArrivedEvent is not None:
			self.OnDataArrivedEvent(ws, packet)
	
	def Send(self, ws_id, data):
		if ws_id in self.ApplicationSockets:
			try:
				self.ApplicationSockets[ws_id].send(json.dumps(data))
			except Exception as e:
				print ("({classname})# [ERROR] Send {0}".format(str(e), classname=self.ClassName))
		else:
			print ("({classname})# [ERROR] This socket ({0}) does not exist. (Might be closed)".format(ws_id, classname=self.ClassName))
	
	def EmitEvent(self, data):
		for key in self.ApplicationSockets:
			self.ApplicationSockets[key].send(json.dumps(data))
	
	def IsServerRunnig(self):
		return self.ServerRunning

	def Worker(self):
		try:
			server = WebSocketServer(('', self.Port), Resource(OrderedDict([('/', WSApplication)])))

			self.ServerRunning = True
			print ("({classname})# Staring local WS server ... {0}".format(self.Port, classname=self.ClassName))
			server.serve_forever()
		except Exception as e:
			print ("({classname})# [ERROR] Stoping local WS server ... {0}".format(str(e), classname=self.ClassName))
			self.ServerRunning = False
	
	def RunServer(self):
		if self.ServerRunning is False:
			_thread.start_new_thread(self.Worker, ())

WSManager = WebsocketLayer()

class WSApplication(WebSocketApplication):
	def __init__(self, *args, **kwargs):
		self.ClassName = "WSApplication"
		super(WSApplication, self).__init__(*args, **kwargs)
	
	def on_open(self):
		print ("({classname})# CONNECTION OPENED".format(classname=self.ClassName))
		WSManager.AppendSocket(id(self.ws), self.ws)

	def on_message(self, message):
		# print ("({classname})# MESSAGE RECIEVED {0} {1}".format(id(self.ws),message,classname=self.ClassName))
		if message is not None:
			WSManager.WSDataArrived(self.ws, message)
		else:
			print ("({classname})# [ERROR] Message is not valid".format(classname=self.ClassName))

	def on_close(self, reason):
		print ("({classname})# CONNECTION CLOSED".format(classname=self.ClassName))
		WSManager.RemoveSocket(id(self.ws))

class ApplicationLayer(definitions.ILayer):
	def __init__(self):
		definitions.ILayer.__init__(self)
		self.WSHandlers = None
		self.Ip 	    = None
		self.Port 	    = None
	
	def SetIp(self, ip):
		self.Ip = ip
	
	def SetPort(self, port):
		self.Port = port
	
	def Run(self):
		# Data for the pages.
		web_data = {
			'ip': str("localhost"),
			'port': str(1981)
		}
		data = json.dumps(web_data)
		web	= webserver.WebInterface("Context", 8181)
		web.AddEndpoint("/", "index", None, data)
		web.Run()

		self.Start()

		time.sleep(0.5)
		WSManager.RegisterCallbacks(self.WSConnectedHandler, self.WSDataArrivedHandler, self.WSDisconnectedHandler, self.WSSessionsEmpty)
		WSManager.SetPort(1981)
		WSManager.RunServer()
	
	def WSConnectedHandler(self, ws_id):
		pass

	def WSDataArrivedHandler(self, ws, packet):
		try:
			command = packet["header"]["command"]
			if self.WSHandlers is not None:
				if command in self.WSHandlers.keys():
					message = self.WSHandlers[command](ws, packet)
					if message == "" or message is None:
						return
					packet["payload"] = message
					WSManager.Send(id(ws), packet)
		except Exception as e:
			print("WSDataArrivedHandler Exception: {0}".format(str(e)))

	def WSDisconnectedHandler(self, ws_id):
		pass

	def WSSessionsEmpty(self):
		pass

	def EmitEvent(self, payload):
		packet = {
			'header': {
				'command': 'event',
				'timestamp': str(int(time.time())),
				'identifier': -1
			},
			'payload': payload
		}
		WSManager.EmitEvent(packet)

class Application(ApplicationLayer):
	def __init__(self):
		ApplicationLayer.__init__(self)
		self.WSHandlers 	= {
			'system_info':			self.SystemInfoHandler,
			'gateway_info': 		self.GatewayInfoHandler,
			'list': 				self.SerialListHandler,
			'connect': 				self.ConnectHandler,
			'disconnect': 			self.DisconnectHandler,
			# NODE UART CONNECTED
			"setworkingport": 		self.SetWorkingPortHandler,
			"getdevicetype": 		self.GetDeviceTypeHandler,
			"getdeviceadditional": 	self.GetDeviceAdditionalHandler,
			"setnodeaddress": 		self.SetNodeAddressHandler,
			"getnodeaddress": 		self.GetNodeAddressHandler,
			"getnodeinfo": 			self.GetNodeInfoHandler,
			"listnodes":			self.GetNodeListHandler,
			"getnodesmap": 			self.GetNodesMapHandler,
			"addnodeindex": 		self.AddNodeIndexHandler,
			"delnodeindex": 		self.DelNodeIndexHandler,
			# NODE REMOTE CONNECTED
			"getnodeinfo_r":		self.GetRemoteNodeInfoHandler,
			"getnodedata_r":		self.GetRemoteNodeDataHandler,
			"setnodedata_r":		self.SetRemoteNodeDataHandler,
			"setnodeaddress_r": 	self.SetRemoteNodeAddressHandler,
			"getnodeaddress_r": 	self.GetRemoteNodeAddressHandler,
		}
		self.HW 			= None
		self.DB 			= sensordb.SensorDB("sensors.db")
		self.Translator 	= translator.BasicTranslator()

		self.WorkingPort = ""
		self.LocalUsbDb = {
			"comports": [],
			"device_id_list": [],
			"gateways": {},
			"nodes": {}
		}

		self.Working = False
	
	def Start(self):
		_thread.start_new_thread(self.Worker, ())
	
	def Worker(self):
		self.Working = True
		while self.Working is True:
			try:
				added, removed = self.CheckSerialConnections()
				if removed is not None:
					self.RemoveDisconnected(removed)
				if added is not None:
					self.ConnectNewComDevices(added)
				time.sleep(5)
			except Exception as e:
				print("Worker Exception: {0}".format(e))
	
	def RemoveGateway(self, comport):
		if comport in self.LocalUsbDb["gateways"]:
			self.EmitEvent({
				"event": "USBDeviceDisconnectedHandler",
				"data": {
					"type": "GATEWAY",
					"port": self.LocalUsbDb["gateways"][comport]["port"],
					"index": self.LocalUsbDb["gateways"][comport]["index"],
				}
			})
			del self.LocalUsbDb["gateways"][comport]
	
	def RemoveNodes(self, comport):
		if comport in self.LocalUsbDb["nodes"]:
			self.EmitEvent({
				"event": "USBDeviceDisconnectedHandler",
				"data": {
					"type": "NODE",
					"port": self.LocalUsbDb["nodes"][comport]["port"],
					"index": self.LocalUsbDb["nodes"][comport]["index"],
				}
			})
			del self.LocalUsbDb["nodes"][comport]

	def RemoveDisconnected(self, removed_ports_list):
		for com in removed_ports_list:
			self.RemoveGateway(com)
			self.RemoveNodes(com)

	def ConnectNewComDevices(self, added_ports_list):
		for com in added_ports_list:
			status = self.HW.SingleConnect(com, 115200)
			if status is True:
				info = self.HW.GetDeviceType(com)
				device_type = info["device_type"]
				if device_type is None:
					self.HW.SingleDisconnect(com)
				else:
					if device_type == "2020":
						info = self.HW.GetDeviceAdditional(com)
						if "type" in info and "index" in info:
							if info["type"] == "GATEWAY":
								self.LocalUsbDb["gateways"][com] = {
									"port": com,
									"index": info["index"],
									"remotes": {}
								}
								self.EmitEvent({
									"event": "USBDeviceConnectedHandler",
									"data": {
										"type": "GATEWAY",
										"port": com,
										"index": info["index"],
									}
								})
								data_nodes = self.HW.GetNodeList(com)
								if data_nodes is not None:
									for node in data_nodes["list"]:
										device_id = node["device_id"]
										self.LocalUsbDb["gateways"][com]["remotes"][device_id] = {
											"status": node["status"],
											"info": None
										}
							elif info["type"] == "NODE":
								self.LocalUsbDb["nodes"][com] = {
									"port": com,
									"index": info["index"],
									"sensors": None
								}
								self.EmitEvent({
									"event": "USBDeviceConnectedHandler",
									"data": {
										"type": "NODE",
										"port": com,
										"index": info["index"],
									}
								})
					else:
						self.HW.SingleDisconnect(com)

	def CheckSerialConnections(self):
		current_ports = []
		data = self.HW.ListSerialComPorts()
		local_db_ports = self.LocalUsbDb["comports"]
		for comp in data:
			current_ports.append(comp["port"])
		added, removed = common.DiffArray(local_db_ports, current_ports)
		if added is not None or removed is not None:
			self.LocalUsbDb["comports"] = current_ports
		return added, removed

	def RegisterHardware(self, hw_layer):
		self.HW = hw_layer
	
	def SystemInfoHandler(self, sock, packet):
		print("SystemInfoHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		data = {
			"event": "SystemInfoHandler",
			"data": {
				"system": {
					"local_db": self.LocalUsbDb
				}
			}
		}
		if is_async is True:
			self.EmitEvent(data)
			return None
		else:
			return data

	def GatewayInfoHandler(self, sock, packet):
		print("GatewayInfoHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		data = {
			"event": "GatewayInfoHandler",
			"data": {
				"gateway": self.LocalUsbDb["gateways"]
			}
		}
		if is_async is True:
			self.EmitEvent(data)
			return None
		else:
			return data
	
	def SerialListHandler(self, sock, packet):
		print("SerialListHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		data = self.HW.ListSerialComPorts()
		if is_async is True:
			self.EmitEvent({
				"event": "SerialListHandler",
				"data": data
			})
			return None
		else:
			return data
	
	def ConnectHandler(self, sock, packet):
		print("ConnectHandler {0}".format(packet))
		is_async 	= packet["payload"]["async"]
		port 		= packet["payload"]["port"]
		baudrate 	= packet["payload"]["baudrate"]

		print("Connect serial port {0} baudrate {1}".format(port, baudrate))
		status = self.HW.SingleConnect(port, baudrate)
		if status is False:
			print("Connection FAILED.")
		else:
			print("Connection SUCCESS.")
		
		data = {
			'event': "ConnectHandler",
			'data': status
		}

		if is_async is True:
			self.EmitEvent(data)
			return None
		else:
			return data
	
	def DisconnectHandler(self, sock, packet):
		print("DisconnectHandler {0}".format(packet))
		is_async 	= packet["payload"]["async"]
		port 		= packet["payload"]["port"]

		print("Disconnect serial port {0}".format(port))
		status = self.HW.SingleDisconnect(port)
		if status is False:
			print("Disconnect FAILED.")
		else:
			print("Disconnect SUCCESS.")
		
		data = {
			'event': "DisconnectHandler",
			'data': status
		}

		if is_async is True:
			self.EmitEvent(data)
			return None
		else:
			return data
	
	def SetWorkingPortHandler(self, sock, packet):
		print("SetWorkingPortHandler {0}".format(packet))
		is_async 			= packet["payload"]["async"]
		self.WorkingPort 	= packet["payload"]["port"]

		if is_async is True:
			self.EmitEvent({
				'event': "SetWorkingPortHandler",
				'data': True
			})
			return None
		else:
			return {}
	
	def GetDeviceTypeHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		ans = self.HW.GetDeviceType(self.WorkingPort)
		if is_async is True:
			self.EmitEvent({
				'event': "GetDeviceTypeHandler",
				'data': ans
			})
			return None
		else:
			return ans
	
	def GetDeviceAdditionalHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		ans = self.HW.GetDeviceAdditional(self.WorkingPort)
		if is_async is True:
			self.EmitEvent({
				'event': "GetDeviceAdditionalHandler",
				'data': ans
			})
			return None
		else:
			return ans
	
	def SetNodeAddressHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		address = packet["payload"]["address"]
		if address is not None:
			ans = self.HW.SetNodeAddress(self.WorkingPort, address)
			if is_async is True:
				self.EmitEvent({
					'event': "SetNodeAddressHandler",
					'data': ans
				})
				return None
			else:
				return ans
		else:
			return None
	
	def GetNodeAddressHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		ans = self.HW.GetNodeAddress(self.WorkingPort)
		if is_async is True:
			self.EmitEvent({
				'event': "GetNodeAddressHandler",
				'data': ans
			})
			return None
		else:
			return ans
	
	def GetNodeInfoHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		ans = self.HW.GetNodeInfo(self.WorkingPort)
		if is_async is True:
			self.EmitEvent({
				'event': "GetNodeInfoHandler",
				'data': ans
			})
			return None
		else:
			return ans
	
	def GetNodesMapHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		ans = (self.HW.GetNodesMap(self.WorkingPort))
		if is_async is True:
			self.EmitEvent({
				'event': "GetNodesMapHandler",
				'data': ans
			})
			return None
		else:
			return ans
	
	def AddNodeIndexHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		index = packet["payload"]["index"]
		if index is not None:
			ans = self.HW.AddNodeIndex(self.WorkingPort, index)
			if ans is not None:
				#TODO - Update DB with new registered sensor id
				if ans["status"] is True:
					self.LocalUsbDb["gateways"][self.WorkingPort]["remotes"][index] = {
						"status": 0,
						"info": None
					}
				if is_async is True:
					self.EmitEvent({
						'event': "AddNodeIndexHandler",
						'data': ans
					})
					return None
				else:
					return ans
			else:
				return None
		else:
			return None
	
	def DelNodeIndexHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		index = packet["payload"]["index"]
		if index is not None:
			ans = self.HW.DelNodeIndex(self.WorkingPort, index)
			if ans is not None:
				#TODO - Update DB with unregistered sensor id
				if ans["status"] is True:
					del self.LocalUsbDb["gateways"][self.WorkingPort]["remotes"][index]
				if is_async is True:
					self.EmitEvent({
						'event': "DelNodeIndexHandler",
						'data': ans
					})
					return None
				else:
					return ans
			else:
				return None
		else:
			return None
	
	def SetRemoteNodeAddressHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		address = packet["payload"]["address"]
		node_id = packet["payload"]["node_id"]
		if address is not None and node_id is not None:
			ans = self.HW.SetRemoteNodeAddress(self.WorkingPort, node_id, address)
			if is_async is True:
				self.EmitEvent({
					'event': "SetRemoteNodeAddressHandler",
					'data': ans
				})
				return None
			else:
				return ans
		else:
			return None
	
	def GetRemoteNodeAddressHandler(self, sock, packet):
		is_async = packet["payload"]["async"]
		node_id = packet["payload"]["node_id"]
		if node_id is not None:
			ans = self.HW.GetRemoteNodeAddress(self.WorkingPort, node_id)
			if is_async is True:
				self.EmitEvent({
					'event': "GetRemoteNodeAddressHandler",
					'data': ans
				})
				return None
			else:
				return ans
		else:
			return None

	def GetNodeListHandler(self, sock, packet):
		print("GetNodeListHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		ans = self.HW.GetNodeList(self.WorkingPort)
		if ans is not None:
			for node in ans["list"]:
				device_id = node["device_id"]
				if device_id in self.LocalUsbDb["gateways"][self.WorkingPort]["remotes"]:
					self.LocalUsbDb["gateways"][self.WorkingPort]["remotes"][device_id]["status"] = node["status"]
				else:
					self.LocalUsbDb["gateways"][self.WorkingPort]["remotes"][device_id] = {
						"status": node["status"],
						"info": None
					}
			data = {
				'event': "GetNodeListHandler",
				'data': ans
			}
			if is_async is True:
				self.EmitEvent(data)
				return None
			else:
				return data
		else:
			return None
	
	def GetRemoteNodeInfoHandler(self, sock, packet):
		print("GetRemoteNodeInfoHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		node_id  = packet["payload"]["node_id"]
		ans = self.HW.GetRemoteNodeInfo(self.WorkingPort, node_id)
		if ans is not None:
			info = self.Translator.Translate(ans["packet"])
			data = {
				'event': "GetRemoteNodeInfoHandler",
				'data': info
			}

			if is_async is True:
				self.EmitEvent(data)
				return None
			else:
				return info
		else:
			return {
				"error": True
			}
	
	def GetRemoteNodeDataHandler(self, sock, packet):
		print("GetRemoteNodeDataHandler {0}".format(packet))
		is_async 	 = packet["payload"]["async"]
		node_id  	 = packet["payload"]["node_id"]
		sensor_index = packet["payload"]["sensor_index"]

		ans = self.HW.GetRemoteNodeData(self.WorkingPort, node_id, sensor_index)
		if ans is not None:
			info = self.Translator.Translate(ans["packet"])
			data = {
				'event': "GetRemoteNodeDataHandler",
				'data': info
			}

			if is_async is True:
				self.EmitEvent(data)
				return None
			else:
				return info
		else:
			return {
				"error": True
			}
	
	def SetRemoteNodeDataHandler(self, sock, packet):
		print("GetRemoteNodeDataHandler {0}".format(packet))
		is_async 	 = packet["payload"]["async"]
		node_id  	 = packet["payload"]["node_id"]
		sensor_index = packet["payload"]["sensor_index"]
		sensor_value = packet["payload"]["sensor_value"]

		ans = self.HW.SetRemoteNodeData(self.WorkingPort, node_id, sensor_index, sensor_value)
		if ans is not None:
			info = self.Translator.Translate(ans["packet"])
			data = {
				'event': "SetRemoteNodeDataHandler",
				'data': info
			}

			if is_async is True:
				self.EmitEvent(data)
				return None
			else:
				return info
		else:
			return {
				"error": True
			}
	
	'''
	Recieve UART packet (pay attention NOT nrf)
	[direction, op_code, content_length, [0...15]]
	'''
	def AsyncDataArrived(self, path, packet):
		# 1. Data from sensors (NRF protocol)
		# 2. Data from Gateway (Other protocol)
		if len(packet) == 19:
			info = self.Translator.Translate(packet[3:])
			if info is not None:
				device_id = int(info["device_id"])
				timestamp = int(time.time())
				info["timestamp"] = timestamp
				info["port"] = path
				# Emit this event to browser
				self.EmitEvent({
					"event": "AsyncDataArrived",
					"data": info
				})
				# Update sensor values for this gateway
				if path in self.LocalUsbDb["gateways"]:
					if device_id in self.LocalUsbDb["gateways"][path]["remotes"]:
						self.LocalUsbDb["gateways"][path]["remotes"][device_id]["info"] = info
						self.LocalUsbDb["gateways"][path]["remotes"][device_id]["status"] = 1
				self.DB.InsertSensorValue({
					'id': 1,
					'device_id': device_id,
					'value': float(info["temperature"]),
					'timestamp': timestamp
				})
				self.DB.InsertSensorValue({
					'id': 2,
					'device_id': device_id,
					'value': float(info["humidity"]),
					'timestamp': timestamp
				})
				self.DB.InsertSensorValue({
					'id': 3,
					'device_id': device_id,
					'value': float(info["movement"]),
					'timestamp': timestamp
				})
				self.DB.InsertSensorValue({
					'id': 4,
					'device_id': device_id,
					'value': float(info["relay"]),
					'timestamp': timestamp
				})