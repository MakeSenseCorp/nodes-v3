#!/usr/bin/python
import signal
import argparse
import struct
import time
import MkSConnectorUART

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

	def SetNodeDataCommand(self, index, data):
		return struct.pack("BBBBBIBB", 0xDE, 0xAD, 0x1, self.OPCODE_SET_NODES_DATA, index, data, 0xAD, 0xDE)
	
	def GetNodeDataCommand(self, index):
		return struct.pack("BBBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODES_DATA, index, 0xAD, 0xDE)
	
	def GetNodeListCommand(self):
		return struct.pack("BBBBBB", 0xDE, 0xAD, 0x1, self.OPCODE_GET_NODES_LIST, 0xAD, 0xDE)
	
	def ReadRemoteCommand(self, node_id, msg):
		s_msg = ''.join(chr(x) for x in msg)
		return struct.pack("BBBBBB{0}sBB".format(len(msg)), 0xDE, 0xAD, 0x1, self.OPCODE_RX_DATA, 1, node_id, s_msg, 0xAD, 0xDE)
	
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

class Terminal():
	def __init__(self):
		self.Commands = NRFCommands()
		self.HW = MkSConnectorUART.Connector()

		self.HW.AdaptorDisconnectedEvent 	= self.AdaptorDisconnectedCallback
		self.HW.AdaptorAsyncDataEvent		= self.AdaptorAsyncDataCallback

		self.Handlers = {
			"help": 					self.HelpHandler,
			"list": 					self.ListHandler,
			"connect": 					self.ConnectHandler,
			"disconnect": 				self.DisconnectHandler,
			"exit": 					self.ExitHandler,
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
			"setworkingnode_r": 		self.SetWorkingNodeIdHandler,
			"getnodeinfo_r": 			self.GetRemoteNodeInfoNodeHandler,
			"getnodedata_r": 			self.GetNodeDataHandler,
			"setnodedata_r": 			self.SetNodeDataHandler,
			"setnodeaddress_r": 		self.UndefinedHandler,
			"getnodeaddress_r": 		self.UndefinedHandler
		}

		self.NodeTypeMap = {
			0x2: "GATEWAY",
			0x3: "NODE"
		}

		self.ProcessRunning = True
		self.WorkingPort = ""
		self.RemoteNodeId = 0
	
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
			if len(packet) > 0:
				if packet[1] == self.Commands.OPCODE_DEL_NODE_INDEX:
					print("Packet: {0}".format(packet))
				else:
					print("(ERROR) Return OPCODE is incorrect.")
			else:
				print("(ERROR) Return packet is less then expected.")
		else:
			print("Wrong parameter")

	def SetWorkingNodeIdHandler(self, data):
		if len(data) > 0:
			self.RemoteNodeId = int(data[0])
		else:
			print("Wrong parameter")

	def GetRemoteNodeInfoNodeHandler(self, data):
		payload = [self.Commands.OPCODE_GET_NODE_INFO]
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)
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
	
	def GetNodeDataHandler(self, data):
		payload = [self.Commands.OPCODE_GET_NODES_DATA]
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				print("Packet: {0}".format(packet))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")

	def SetNodeDataHandler(self, data):
		index = int(data[0])
		value = int(data[1])
		payload = [self.Commands.OPCODE_SET_NODES_DATA, index, value]
		packet = self.Commands.ReadRemoteCommand(self.RemoteNodeId, payload)
		packet = self.HW.Send(self.WorkingPort, packet)
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				print("Packet: {0}".format(packet))
			else:
				print("(ERROR) Return OPCODE is incorrect.")
		else:
			print("(ERROR) Return packet is less then expected.")

	def AdaptorAsyncDataCallback(self, path, packet):
		pass

	def AdaptorDisconnectedCallback(self, path, rf_type):
		pass

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

	terminal = Terminal()
	
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

	while(terminal.ProcessRunning is True):
		try:
			raw  	= raw_input('> ')
			data 	= raw.split(" ")
			cmd  	= data[0]
			params 	= data[1:]

			if cmd in terminal.Handlers:
				terminal.Handlers[cmd](params)
			else:
				if cmd not in [""]:
					print("unknown command")
		except Exception as e:
			print("{0}".format(e))

	terminal.Close()
	print("Bye.")

if __name__ == "__main__":
    main()

