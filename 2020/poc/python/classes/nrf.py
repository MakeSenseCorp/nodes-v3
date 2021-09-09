import struct
from classes import hardware
from classes import common

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

class NRF(hardware.HardwareLayer):
	def __init__(self):
		hardware.HardwareLayer.__init__(self)
		self.Commands = NRFCommands()

		self.NodeTypeMap = {
			0x2: "GATEWAY",
			0x3: "NODE"
		}
	
	def GetDeviceType(self, port):
		dev_type = self.HW.GetDeviceType(port)
		return {
			'device_type': dev_type
		}
	
	def GetDeviceAdditional(self, port):
		additional = self.HW.GetDeviceAdditional(port)
		if (len(additional) > 1):
			return {
				'type': self.NodeTypeMap[additional[0]],
				'index': additional[1]
			}
		return None
	
	def SetNodeAddress(self, port, address):
		packet = self.Commands.SetAddressCommand(address)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None

		if len(packet) > 3:
			if packet[1] == self.Commands.OPCODE_SET_ADDRESS:
				return {
					'index': packet[3]
				}
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetNodeAddress(self, port):
		packet = self.Commands.GetAddressCommand()
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None
		
		if len(packet) > 3:
			if packet[1] == self.Commands.OPCODE_GET_ADDRESS:
				return {
					'index': packet[3]
				}
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetNodeInfo(self, port):
		packet = self.Commands.GetNodeInfoCommand()
		info = self.HW.Send(port, packet)

		if info is None:
			return None
		
		if len(info) > 3:
			if info[1] == self.Commands.OPCODE_GET_NODE_INFO:
				return {
					'info': info
				}
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetNodeList(self, port):
		packet = self.Commands.GetNodeListCommand()
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None
		
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_GET_NODES_LIST:
				info = {
					'list': []
				}
				data = packet[3:]
				for idx, item in enumerate(data[::2]):
					node = data[idx*2:idx*2+2]
					info["list"].append({
						"device_id": node[0],
						"status": node[1]
					})
				return info
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetNodesMap(self, port):
		packet = self.Commands.GetNodesMapCommand()
		map = self.HW.Send(port, packet)

		if map is None:
			return None
		
		if len(map) > 3:
			if map[1] == self.Commands.OPCODE_GET_NODES_MAP:
				return {
					'info': map
				}
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def AddNodeIndex(self, port, index):
		packet = self.Commands.AddNodeIndexCommand(index)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None

		if len(packet) > 3:
			if packet[1] == self.Commands.OPCODE_ADD_NODE_INDEX:
				updated_index = packet[3]
				status = False
				if index == updated_index:
					status = True
				return {
					'status': status,
					'info': packet
				}
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def DelNodeIndex(self, port, index):
		packet = self.Commands.DelNodeIndexCommand(index)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None

		if len(packet) > 3:
			if packet[1] == self.Commands.OPCODE_DEL_NODE_INDEX:
				updated_index = packet[3]
				status = False
				if index == updated_index:
					status = True
				return {
					'status': status,
					'device_id': updated_index
				}
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetRemoteNodeInfo(self, port, index):
		payload = [self.Commands.OPCODE_GET_NODE_INFO, 0]
		packet = self.Commands.ReadRemoteCommand(index, payload)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None
		
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				if len(packet) > 18:
					if packet[4] == self.Commands.OPCODE_GET_NODE_INFO:
						nrf_packet = packet[3:]
						return {
							'packet': nrf_packet
						}
					else:
						print("(ERROR) Incorrect answer. {0}".format(packet))
						return None
				else:
					print("(ERROR) Packet length incorrect.")
					return None
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetRemoteNodeData(self, port, node_id, sensor_index):
		payload = [self.Commands.OPCODE_GET_NODES_DATA, 1, sensor_index]
		packet = self.Commands.ReadRemoteCommand(node_id, payload)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None
		
		if len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				if packet[4] == self.Commands.OPCODE_GET_NODES_DATA:
					nrf_packet = packet[3:]
					return {
						'packet': nrf_packet
					}
				else:
					print("(ERROR) Incorrect answer. {0}".format(packet))
					return None
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def SetRemoteNodeData(self, port, node_id, sensor_index, sensor_value):
		arr_value = common.IntToBytes(sensor_value, 4)
		# arr_value = value.to_bytes(4, 'big')
		payload = [self.Commands.OPCODE_SET_NODES_DATA, 5, sensor_index] + arr_value
		packet = self.Commands.ReadRemoteCommand(node_id, payload)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None

		if packet is not None and len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				if packet[4] == self.Commands.OPCODE_SET_NODES_DATA:
					nrf_packet = packet[3:]
					return {
						'packet': nrf_packet
					}
				else:
					print("(ERROR) Incorrect answer. {0}".format(packet))
					return None
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def SetRemoteNodeAddress(self, port, node_id, address):
		# OPCODE : LEN : PAYLOAD
		payload = [self.Commands.OPCODE_SET_ADDRESS, 1, address]
		packet = self.Commands.ReadRemoteCommand(node_id, payload)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None
		
		if packet is not None and len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				if packet[4] == self.Commands.OPCODE_SET_ADDRESS:
					return {
						'packet': packet
					}
				else:
					print("(ERROR) Incorrect answer. {0}".format(packet))
					return None
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
	
	def GetRemoteNodeAddress(self, port, node_id):
		payload = [self.Commands.OPCODE_GET_ADDRESS]
		packet = self.Commands.ReadRemoteCommand(node_id, payload)
		packet = self.HW.Send(port, packet)

		if packet is None:
			return None

		if packet is not None and len(packet) > 0:
			if packet[1] == self.Commands.OPCODE_RX_DATA:
				if packet[4] == self.Commands.OPCODE_GET_ADDRESS:
					return {
						'packet': packet
					}
				else:
					print("(ERROR) Incorrect answer. {0}".format(packet))
					return None
			else:
				print("(ERROR) Return OPCODE is incorrect.")
				return None
		else:
			print("(ERROR) Return packet is less then expected.")
			return None
