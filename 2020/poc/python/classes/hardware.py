from classes import definitions
import MkSConnectorUART

class HardwareLayer(definitions.ILayer):
	def __init__(self):
		definitions.ILayer.__init__(self)
		self.HW = MkSConnectorUART.Connector()

		self.Locker			= None
		self.AsyncListeners	= []

		self.HW.AdaptorDisconnectedEvent 	= self.AdaptorDisconnectedCallback
		self.HW.AdaptorAsyncDataEvent		= self.AdaptorAsyncDataCallback
	
	def AdaptorAsyncDataCallback(self, path, packet):
		pass

	def AdaptorDisconnectedCallback(self, path, rf_type):
		pass

	def RegisterListener(self, callback):
		pass

	def RemoveListener(self, callback):
		pass

	def ListSerialComPorts(self):
		return self.HW.ListSerialComPorts()

	def SingleConnect(self, port, baudrate):
		return self.HW.SingleConnect(port, baudrate)
	
	def SingleDisconnect(self, port):
		return self.HW.SingleDisconnect(port)
	
	def Disconnect(self):
		self.HW.Disconnect()
	
	def GetDeviceType(self, port):
		return self.HW.GetDeviceType(port)
	
	def GetDeviceAdditional(self, port):
		return self.HW.GetDeviceAdditional(port)
