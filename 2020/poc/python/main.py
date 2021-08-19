#!/usr/bin/python
import signal
import argparse
import struct
import time

import _thread
import json
import subprocess

import MkSConnectorUART
import MkSLogger
import MkSLocalWebServer

from classes import definitions

from collections import OrderedDict
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
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

class NRFTask(definitions.ITask):
	def __init__(self):
		definitions.ITask.__init__(self, "NRFTask")
		self.Name = "NRFTask"
	
	def Handler(self):
		pass

class NRFCommands():
	def __init__(self):
		self.OPCODE_RX_DATA			= 100
		self.OPCODE_TX_DATA			= 101
		self.OPCODE_SET_ADDRESS 	= 102
		self.OPCODE_GET_ADDRESS 	= 103
		self.OPCODE_GET_NODEMAP 	= 104
		self.OPCODE_ADD_NODE_INDEX 	= 105
		self.OPCODE_DEL_NODE_INDEX 	= 106
		self.OPCODE_GET_NODE_INFO 	= 107
		self.OPCODE_GET_NODES_MAP 	= 108
		self.OPCODE_GET_NODES_LIST	= 109
		self.OPCODE_SET_NODES_DATA	= 110
		self.OPCODE_GET_NODES_DATA	= 111
	
	'''
	{UART PACKET}
	-------------
	[MAGIC_NUMBER] 		(2 Bytes)
	[Direction] 		(1 Byte)
	[Opcode]			(1 Byte)
	[Content Length] 	(1 Byte)
	[Payload]			(57 Bytes)
	[MAGIC_NUMBER] 		(2 Bytes)

	{NRF PACKET}
	------------
	[NodeID] 			(1 Byte)
	[Opcode] 			(1 Byte)
	[Size] 				(1 Byte)
	[Payload]			(12 Bytes)
	[CRC] 				(1 Byte)
	'''

	def SetNodeDataCommand(self, index, data):
		return struct.pack("BBBBBIBB", 0xDE, 0xAD, 0x1, self.OPCODE_SET_NODES_DATA, index, data, 0xAD, 0xDE)
	
	def GetNodeDataCommand(self, index):
		return struct.pack("BBBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODES_DATA, index, 0xAD, 0xDE)
	
	def GetNodeListCommand(self):
		return struct.pack("BBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODES_LIST, 0xAD, 0xDE)
	
	def ReadRemoteCommand(self, node_id, msg):
		s_msg = ''.join(chr(x) for x in msg)
		# 													   [MN]    [DIR]          [OP]     [LEN]   [ID]   [OP] [LEN] [P]     [MN]
		return struct.pack("BBBBBB{0}sBB".format(len(msg)), 0xDE, 0xAD, 0x1, self.OPCODE_RX_DATA, 1, node_id, s_msg.encode(), 0xAD, 0xDE)
	
	def WriteRemoteCommand(self, node_id):
		return struct.pack("BBBBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_TX_DATA, 1, node_id, 0xAD, 0xDE)

	def GetNodeMapCommand(self):
		return struct.pack("BBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODEMAP, 0xAD, 0xDE)
	
	def AddNodeIndexCommand(self, index):
		return struct.pack("BBBBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_ADD_NODE_INDEX, 1, index, 0xAD, 0xDE)
	
	def DelNodeIndexCommand(self, index):
		return struct.pack("BBBBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_DEL_NODE_INDEX, 1, index, 0xAD, 0xDE)

	def SetAddressCommand(self, address):
		return struct.pack("BBBBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_SET_ADDRESS, 1, address, 0xAD, 0xDE)
	
	def GetAddressCommand(self):
		return struct.pack("BBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_ADDRESS, 0xAD, 0xDE)
	
	def GetNodeInfoCommand(self):
		return struct.pack("BBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODE_INFO, 0xAD, 0xDE)
	
	def GetNodesMapCommand(self):
		return struct.pack("BBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODES_MAP, 0xAD, 0xDE)

class HardwareLayer(definitions.ILayer):
	def __init__(self):
		definitions.ILayer.__init__(self)

		self.Commands 	= NRFCommands()
		self.HW 		= MkSConnectorUART.Connector()

		self.Locker			= None
		self.AsyncListeners	= []

		self.HW.AdaptorDisconnectedEvent 	= self.AdaptorDisconnectedCallback
		self.HW.AdaptorAsyncDataEvent		= self.AdaptorAsyncDataCallback
	
	def AdaptorAsyncDataCallback(self, path, packet):
		print(packet)

	def AdaptorDisconnectedCallback(self, path, rf_type):
		pass

	def RegisterListener(self, callback):
		pass

	def RemoveListener(self, callback):
		pass

class ApplicationLayer(definitions.ILayer):
	def __init__(self):
		definitions.ILayer.__init__(self)
		self.WSHandlers = {
			'gateway_info': self.GayewayInfoHandler,
		}
		self.Ip 	= None
		self.Port 	= None
		self.HW 	= None
	
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
		web	= MkSLocalWebServer.WebInterface("Context", 8181)
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
		if command in self.WSHandlers.keys():
			message = self.WSHandlers[command](ws, packet)
			if message == "" or message is None:
				return
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

	def RegisterHardware(self, hw_layer):
		self.HW = hw_layer
	
	def GayewayInfoHandler(self, sock, packet):
		print("GayewayInfoHandler {0}".format(packet))
		payload = packet["payload"]

		return {
			"gateway": {
				"connected": []
			}
		}

class TerminalLayer():
	def __init__(self):
		self.Commands 		= NRFCommands()
		self.HW 			= MkSConnectorUART.Connector()

		self.HW.AdaptorDisconnectedEvent 	= self.AdaptorDisconnectedCallback
		self.HW.AdaptorAsyncDataEvent		= self.AdaptorAsyncDataCallback

		self.WSHandlers = {
			'gateway_info': self.GayewayInfoHandler,
		}

		self.Tasks = {
			"NRFTask": NRFTask()
		}

		self.Handlers = {
			"help": 					self.HelpHandler,
			"list": 					self.ListHandler,
			"connect": 					self.ConnectHandler,
			"disconnect": 				self.DisconnectHandler,
			"exit": 					self.ExitHandler,
			"task":						self.TasksHandler,
			"app":						self.AppHandler,
			# NODE UART CONNECTED
			"setworkingport": 			self.SetWorkingPortHandler,
			"getdevicetype": 			self.GetDeviceTypeHandler,
			"getdeviceadditional": 		self.GetDeviceAdditionalHandler,
			"setnodeaddress": 			self.SetNodeAddressHandler,
			"getnodeaddress": 			self.GetNodeAddressHandler,
			"getnodeinfo": 				self.GetNodeInfoHandler,
			"listnodes": 				self.GetNodeListHandler,
			"getnodesmap": 				self.GetNodesMapHandler,
			"addnodeindex": 			self.AddNodeIndexHandler,
			"delnodeindex": 			self.DelNodeIndexHandler,
			# NODE REMOTE CONNECTED
			"setworkingnode_r": 		self.SetRemoteWorkingNodeIdHandler,
			"getnodeinfo_r": 			self.GetRemoteNodeInfoNodeHandler,
			"getnodedata_r": 			self.GetRemoteNodeDataHandler,
			"setnodedata_r": 			self.SetRemoteNodeDataHandler,
			"setnodeaddress_r": 		self.SetRemoteNodeAddressHandler,
			"getnodeaddress_r": 		self.GetRemoteNodeAddressHandler
		}

		self.NodeTypeMap = {
			0x2: "GATEWAY",
			0x3: "NODE"
		}

		self.ProcessRunning = True
		self.WorkingPort = ""
		self.RemoteNodeId = 0
	
	def RegisterHardware(self, hw_layer):
		self.HW = hw_layer
	
	def Close(self):
		self.HW.Disconnect()

	def UndefinedHandler(self, data):
		pass

	def ExitHandler(self, data):
		self.ProcessRunning = False

	def DisconnectHandler(self, data):
		if len(data) > 0:
			port = data[0]
			print("Disconnect serial port {0}".format(port))
			status = self.HW.SingleDisconnect(port)
			if status is False:
				print("Disconnect FAILED")
			else:
				print("Disconnect SUCCESS")
		else:
			print("Wrong parameter")

	def ConnectHandler(self, data):
		if len(data) > 1:
			port = data[0]
			baudrate = int(data[1])
			print("Connect serial port {0} baudrate {1}".format(port, baudrate))
			status = self.HW.SingleConnect(port, baudrate)
			if status is False:
				print("Connection FAILED.")
			else:
				print("Connection SUCCESS.")
		else:
			print("Wrong parameter")

	def ListHandler(self, data):
		comports = self.HW.ListSerialComPorts()
		for idx, comport in enumerate(comports):
			print("{0}.\tComPort: {1}\n\tConnected: {2}\n\tType: {3}\n".format(idx+1, comport["port"], comport["is_connected"], comport["type"]))
		self.EmitEvent({
			'event': "ListHandler",
			'data': comports
		})

	def HelpHandler(self, data):
		pass

	def SetWorkingPortHandler(self, data):
		if len(data) > 0:
			self.WorkingPort = data[0]
		else:
			print("Wrong parameter")

	def GetDeviceTypeHandler(self, data):
		print(self.HW.GetDeviceType(self.WorkingPort))

	def SetNodeAddressHandler(self, data):
		if len(data) > 0:
			address = int(data[0])
			packet = self.Commands.SetAddressCommand(address)
			packet = self.HW.Send(self.WorkingPort, packet)

			if packet is None:
				return

			if len(packet) > 3:
				if packet[1] == self.Commands.OPCODE_SET_ADDRESS:
					print("Node index set to {0}".format(packet[3]))
				else:
					print("(ERROR) Return OPCODE is incorrect.")
			else:
				print("(ERROR) Return packet is less then expected.")
		else:
			print("Wrong parameter")
	
	def GetNodeAddressHandler(self, data):
		packet = self.Commands.GetAddressCommand()
		packet = self.HW.Send(self.WorkingPort, packet)

		if packet is None:
			return
		
		if len(packet) > 3:
			if packet[1] == self.Commands.OPCODE_GET_ADDRESS:
				print("Node index: {0}".format(packet[3]))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")

	def GetDeviceAdditionalHandler(self, data):
		additional = self.HW.GetDeviceAdditional(self.WorkingPort)
		node_type  = additional[0]
		node_index = additional[1]
		print("Node type: {0}\nNode index: {1}".format(self.NodeTypeMap[node_type], node_index))
	
	def GetNodeInfoHandler(self, data):
		packet = self.Commands.GetNodeInfoCommand()
		info = self.HW.Send(self.WorkingPort, packet)

		if info is None:
			return
		
		if len(info) > 3:
			if info[1] == self.Commands.OPCODE_GET_NODE_INFO:
				print("Node Info: {0}".format(info))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")
	
	def GetNodesMapHandler(self, data):
		packet = self.Commands.GetNodesMapCommand()
		map = self.HW.Send(self.WorkingPort, packet)

		if map is None:
			return
		
		if len(map) > 3:
			if map[1] == self.Commands.OPCODE_GET_NODES_MAP:
				print("Map: {0}".format(map))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")
	
	def AddNodeIndexHandler(self, data):
		if len(data) > 0:
			index = int(data[0])
			packet = self.Commands.AddNodeIndexCommand(index)
			packet = self.HW.Send(self.WorkingPort, packet)

			if packet is None:
				return

			if len(packet) > 0:
				if packet[1] == self.Commands.OPCODE_ADD_NODE_INDEX:
					print("Packet: {0}".format(packet))
				else:
					print("(ERROR) Return OPCODE is incorrect.")
			else:
				print("(ERROR) Return packet is less then expected.")
		else:
			print("Wrong parameter")
	
	def DelNodeIndexHandler(self, data):
		if len(data) > 0:
			index = int(data[0])
			packet = self.Commands.DelNodeIndexCommand(index)
			packet = self.HW.Send(self.WorkingPort, packet)

			if packet is None:
				return

			if len(packet) > 0:
				if packet[1] == self.Commands.OPCODE_DEL_NODE_INDEX:
					print("Packet: {0}".format(packet))
				else:
					print("(ERROR) Return OPCODE is incorrect.")
			else:
				print("(ERROR) Return packet is less then expected.")
		else:
			print("Wrong parameter")

	def SetRemoteWorkingNodeIdHandler(self, data):
		if len(data) > 0:
			self.RemoteNodeId = int(data[0])
		else:
			print("Wrong parameter")

	def GetRemoteNodeInfoNodeHandler(self, data):
		payload = [self.Commands.OPCODE_GET_NODE_INFO, 0]
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)

		if packet is None:
			return
		
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				print("Packet: {0}".format(packet))
				if len(packet) > 18:
					nrf_packet = packet[6:]
					if nrf_packet[0] == 50:
						# Temperature, Humidity & Relay
						temperature = nrf_packet[3] | nrf_packet[4] << 8
						humidity 	= nrf_packet[6] | nrf_packet[7] << 8
						relay 		= nrf_packet[9]
						print("Sensor type: Temperature, Humidity & Relay (50)\nTemperature: {0}\nHumidity: {1}\nRelay: {2}".format(temperature,humidity,relay))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")
	
	def GetNodeListHandler(self, data):
		packet = self.Commands.GetNodeListCommand()
		packet = self.HW.Send(self.WorkingPort, packet)

		if packet is None:
			return
		
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_GET_NODES_LIST:
				print("Packet: {0}".format(packet))
				data = packet[3:]
				for idx, item in enumerate(data[::2]):
					print(data[idx*2:idx*2+2])
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")
	
	def GetRemoteNodeDataHandler(self, data):
		payload = [self.Commands.OPCODE_GET_NODES_DATA]
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)

		if packet is None:
			return
		
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				print("Packet: {0}".format(packet))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")
	
	def IntToBytes(self, value, length):
		byte_array = []
		while value != 0:
			byte_array = [value % 256] + byte_array
			value = value // 256
		
		# ATMEL will read data from left to right
		byte_array = byte_array + [0]*(length-len(byte_array))
		return byte_array

	def SetRemoteNodeDataHandler(self, data):
		index = int(data[0])
		value = int(data[1])
		#arr_value = value.to_bytes(4, 'big')
		arr_value = self.IntToBytes(value, 4)
		payload = [self.Commands.OPCODE_SET_NODES_DATA, 5, index] + arr_value
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)
		if packet is not None and len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				print("Packet: {0}".format(packet))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")
	
	def SetRemoteNodeAddressHandler(self, data):
		if len(data) > 0:
			address = int(data[0])
			# OPCODE : LEN : PAYLOAD
			payload = [self.Commands.OPCODE_SET_ADDRESS, 1, address]
			packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
			packet = self.HW.Send(self.WorkingPort, packet)
			if packet is not None and len(packet) > 0:
				if packet[1] == self.Commands.OPCODE_RX_DATA:
					print("Packet: {0}".format(packet))
				else:
					print("(ERROR) Return OPCODE is incorrect.")
			else:
				print("(ERROR) Return packet is less then expected.")
		else:
			print("Wrong parameter")
	
	def GetRemoteNodeAddressHandler(self, data):
		payload = [self.Commands.OPCODE_GET_ADDRESS]
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)
		if packet is not None and len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				print("Packet: {0}".format(packet))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")

	def TasksHandler(self, data):
		if len(data) > 1:
			name 		= data[0]
			action 		= data[1]

			if name in self.Tasks:
				task = self.Tasks[name]
				if action == "start":
					task.Start()
				elif action == "stop":
					task.Stop()
				elif action == "pause":
					task.Pause()
				elif action == "resume":
					task.Resume()
				else:
					pass
		else:
			print("Wrong parameter")
	
	def AppHandler(self, data):
		subprocess.call(["ui.cmd"])

	def AdaptorAsyncDataCallback(self, path, packet):
		print(packet)

	def AdaptorDisconnectedCallback(self, path, rf_type):
		pass
	
	def WSConnectedHandler(self, ws_id):
		pass

	def WSDataArrivedHandler(self, ws, packet):
		command = packet["header"]["command"]
		if command in self.WSHandlers.keys():
			message = self.WSHandlers[command](ws, packet)
			if message == "" or message is None:
				return
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

	def GayewayInfoHandler(self, sock, packet):
		print("GayewayInfoHandler {0}".format(packet))
		payload = packet["payload"]

		return {
			"gateway": {
				"connected": []
			}
		}

def signal_handler(signal, frame):
	pass
	
def main():
	signal.signal(signal.SIGINT, signal_handler)

	parser = argparse.ArgumentParser(description='Execution module called Node \n Example: python.exe main.py --serial COM31')
	parser.add_argument('-v', '--version', action='store_true',
			help='Version')
	parser.add_argument('-cn', '--serial', action='store',
			dest='serial', help='Serial COM to connect')
	parser.add_argument('-verb', '--verbose', action='store_true',
			help='Print messages')
	
	args = parser.parse_args()

	terminal 	= TerminalLayer()
	app 		= ApplicationLayer()
	gateway 	= HardwareLayer()

	app.RegisterHardware(gateway)
	# terminal.RegisterHardware(gateway)
	
	'''
	com_port = ""
	if args.serial is not None:
		com_port = str(args.serial)
		status = HW.SingleConnect(com_port, 115200)
		if status is False:
			return
	else:
		return
	'''

	# Data for the pages.
	web_data 	= {
		'ip': str("localhost"),
		'port': str(1981)
	}
	data = json.dumps(web_data)
	web	= MkSLocalWebServer.WebInterface("Context", 8181)
	web.AddEndpoint("/", "index", None, data)
	web.Run()

	time.sleep(0.5)
	WSManager.RegisterCallbacks(terminal.WSConnectedHandler, terminal.WSDataArrivedHandler, terminal.WSDisconnectedHandler, terminal.WSSessionsEmpty)
	WSManager.SetPort(1981)
	WSManager.RunServer()

	try:
		while(terminal.ProcessRunning is True):
			raw  	= input('> ')
			data 	= raw.split(" ")
			cmd  	= data[0]
			params 	= data[1:]

			if cmd in terminal.Handlers:
				terminal.Handlers[cmd](params)
				# WSManager.EmitEvent(cmd)
			else:
				if cmd not in [""]:
					print("unknown command")
	except Exception as e:
		print("{0}".format(e))

	terminal.Close()
	print("Bye.")

if __name__ == "__main__":
    main()
