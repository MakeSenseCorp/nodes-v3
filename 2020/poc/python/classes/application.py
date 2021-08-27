import json
import time
import _thread
from collections import OrderedDict
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

from classes import definitions
from classes import webserver
from classes import sensordb
from classes import translator

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

		time.sleep(0.5)
		WSManager.RegisterCallbacks(self.WSConnectedHandler, self.WSDataArrivedHandler, self.WSDisconnectedHandler, self.WSSessionsEmpty)
		WSManager.SetPort(1981)
		WSManager.RunServer()
	
	def WSConnectedHandler(self, ws_id):
		pass

	def WSDataArrivedHandler(self, ws, packet):
		command = packet["header"]["command"]
		if self.WSHandlers is not None:
			if command in self.WSHandlers.keys():
				message = self.WSHandlers[command](ws, packet)
				if message == "" or message is None:
					return
				packet["payload"] = message
				WSManager.Send(id(ws), packet)

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
			'gateway_info': 	self.GayewayInfoHandler,
			'serial_list': 		self.SerialListHandler,
			'connect': 			self.ConnectHandler,
			'disconnect': 		self.DisconnectHandler,
			"setworkingport": 	self.SetWorkingPortHandler,
			"listnodes":		self.GetNodeListHandler,
			"getnodeinfo_r":	self.GetRemoteNodeInfoHandler,
			"getnodedata_r":	self.GetRemoteNodeDataHandler,
			"setnodedata_r":	self.SetRemoteNodeDataHandler,
		}
		self.HW 			= None
		self.DB 			= sensordb.SensorDB("sensors.db")
		self.Translator 	= translator.BasicTranslator()

		self.WorkingPort = ""

	def RegisterHardware(self, hw_layer):
		self.HW = hw_layer
	
	def GayewayInfoHandler(self, sock, packet):
		print("GayewayInfoHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		data = {
			"gateway": {
				"connected": []
			}
		}
		if is_async is True:
			self.EmitEvent(data)
			return None
		else:
			return data
	
	def SerialListHandler(self, sock, packet):
		print("GayewayInfoHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		data = self.HW.ListSerialComPorts()
		if is_async is True:
			self.EmitEvent(data)
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
			self.EmitEvent({})
			return None
		else:
			return {}
	
	def GetNodeListHandler(self, sock, packet):
		print("GetNodeListHandler {0}".format(packet))
		is_async = packet["payload"]["async"]
		ans = self.HW.GetNodeList(self.WorkingPort)
		data = {
			'event': "GetNodeListHandler",
			'data': ans
		}
		if is_async is True:
			self.EmitEvent(data)
			return None
		else:
			return data
	
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
				return data
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
				return data
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
				return data
		else:
			return {
				"error": True
			}
	
	'''
	Recieve UART packet (pay attention NOT nrf)
	[direction, op_code, content_length, [0...15]]
	'''
	def AsyncDataArrived(self, packet):
		if len(packet) == 19:
			info = self.Translator.Translate(packet[3:])
			if info is not None:
				sensor_id = int(info["sensor_id"])
				timestamp = int(time.time())
				info["timestamp"] = timestamp
				# Emit this event to browser
				self.EmitEvent(info)
				self.DB.InsertSensorValue({
					'id': 1,
					'sensor_id': sensor_id,
					'value': float(info["temperature"]),
					'timestamp': timestamp
				})
				self.DB.InsertSensorValue({
					'id': 2,
					'sensor_id': sensor_id,
					'value': float(info["humidity"]),
					'timestamp': timestamp
				})
				self.DB.InsertSensorValue({
					'id': 3,
					'sensor_id': sensor_id,
					'value': float(info["movement"]),
					'timestamp': timestamp
				})
				self.DB.InsertSensorValue({
					'id': 4,
					'sensor_id': sensor_id,
					'value': float(info["relay"]),
					'timestamp': timestamp
				})