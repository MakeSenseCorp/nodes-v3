class BasicTranslator():
	def __init__(self):
		self.ClassName	= "BasicTranslator"
		self.DeviceType = {
			50: self.PTHL
		}

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

		self.RelayActionMap = {
			0: "OFF",
			1: "ON"
		}
	
	'''
	typedef struct {
		uint8_t node_id;
		uint8_t opcode;
		uint8_t size;
		uint8_t payload[12];
		uint8_t crc;
	} message_t;
	payload = [device_type, size, Data[0...11]]
	'''
	def Translate(self, packet):
		if (len(packet) == 16):
			device_type = packet[3]
			if device_type in self.DeviceType:
				handler = self.DeviceType[device_type]
				return handler(packet)
		return None
	
	def PTHL(self, packet):
		if packet[1] == self.OPCODE_GET_NODE_INFO:
			payload = packet[5:-1]
			temperature = payload[1] | payload[2] << 8
			humidity 	= payload[4] | payload[5] << 8
			pir 		= payload[7]
			relay 		= payload[9]
			return {
				'sensor_id': packet[0],
				'temperature': temperature,
				'humidity': humidity,
				'relay': relay,
				'movement': pir,
				'payload': payload
			}
		elif packet[1] == self.OPCODE_SET_NODES_DATA:
			payload = packet[5:-1]
			sensor_type = payload[0]
			sensor_value = payload[1]
			if sensor_type == 4:
				return {
					'sensor_id': packet[0],
					'senor': "relay",
					'value': sensor_value,
					'payload': payload
				}
			else:
				return None
		elif packet[1] == self.OPCODE_GET_NODES_DATA:
			payload = packet[5:-1]
			sensor_type = payload[0]
			if sensor_type == 1:
				return {
					'sensor_id': packet[0],
					'senor': "temperature",
					'value': payload[1] | payload[2] << 8,
					'payload': payload
				}
			if sensor_type == 2:
				return {
					'sensor_id': packet[0],
					'senor': "humidity",
					'value': payload[1] | payload[2] << 8,
					'payload': payload
				}
			if sensor_type == 3:
				return {
					'sensor_id': packet[0],
					'senor': "movement",
					'value': payload[1],
					'payload': payload
				}
			if sensor_type == 4:
				return {
					'sensor_id': packet[0],
					'senor': "relay",
					'value': payload[1],
					'payload': payload
				}
			else:
				return None
		else:
			return None