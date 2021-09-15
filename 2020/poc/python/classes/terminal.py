import subprocess
from classes import definitions
from classes import translator

# import MkSLogger

class NRFTask(definitions.ITask):
	def __init__(self):
		definitions.ITask.__init__(self, "NRFTask")
		self.Name = "NRFTask"
	
	def Handler(self):
		pass

class TerminalLayer(definitions.ILayer):
	def __init__(self):
		definitions.ILayer.__init__(self)
		self.ProcessRunning = True
		self.Handlers = None
	
	def Run(self):	
		try:
			while(self.ProcessRunning is True):
				raw  	= input('> ')
				data 	= raw.split(" ")
				cmd  	= data[0]
				params 	= data[1:]

				if self.Handlers is not None:
					if cmd in self.Handlers:
						self.Handlers[cmd](params)
					else:
						if cmd not in [""]:
							print("unknown command")
		except Exception as e:
			print("Terminal Exception {0}".format(str(e)))
	
	def Exit(self):
		self.ProcessRunning = False

class Terminal(TerminalLayer):
	def __init__(self):
		TerminalLayer.__init__(self)
		self.HW 			= None
		self.Application 	= None
		self.Translator 	= translator.BasicTranslator()

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
			"getnodeinfo_r": 			self.GetRemoteNodeInfoHandler,
			"getnodedata_r": 			self.GetRemoteNodeDataHandler,
			"setnodedata_r": 			self.SetRemoteNodeDataHandler,
			"setnodeaddress_r": 		self.SetRemoteNodeAddressHandler,
			"getnodeaddress_r": 		self.GetRemoteNodeAddressHandler
		}

		self.WorkingPort = ""
		self.RemoteNodeId = 0
	
	def UpdateApplication(self, data):
		if self.Application is not None:
			self.Application.EmitEvent(data)
	
	def RegisterHardware(self, hw_layer):
		self.HW = hw_layer
	
	def RegisterApplication(self, app_layer):
		self.Application = app_layer

	def HelpHandler(self, data):
		pass

	def ListHandler(self, data):
		comports = self.HW.ListSerialComPorts()
		for idx, comport in enumerate(comports):
			print("{0}.\tComPort: {1}\n\tConnected: {2}\n\tType: {3}\n".format(idx+1, comport["port"], comport["is_connected"], comport["type"]))
		self.UpdateApplication({
			'event': "ListHandler",
			'data': comports
		})

	def ConnectHandler(self, data):
		if len(data) > 1:
			port = data[0]
			baudrate = int(data[1])
			print("Connect serial port {0} baudrate {1}".format(port, baudrate))
			status = self.HW.SingleConnect(port, baudrate)
			self.UpdateApplication({
				'event': "ConnectHandler",
				'data': status
			})
			if status is False:
				print("Connection FAILED.")
			else:
				print("Connection SUCCESS.")
		else:
			print("Wrong parameter")

	def DisconnectHandler(self, data):
		if len(data) > 0:
			port = data[0]
			print("Disconnect serial port {0}".format(port))
			status = self.HW.SingleDisconnect(port)
			self.UpdateApplication({
				'event': "DisconnectHandler",
				'data': status
			})
			if status is False:
				print("Disconnect FAILED")
			else:
				print("Disconnect SUCCESS")
		else:
			print("Wrong parameter")
	
	def ExitHandler(self, data):
		self.Exit()
	
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

	def SetWorkingPortHandler(self, data):
		if len(data) > 0:
			self.WorkingPort = data[0]
		else:
			print("Wrong parameter")
	
	def GetDeviceTypeHandler(self, data):
		ans = self.HW.GetDeviceType(self.WorkingPort)
		print(ans)
		self.UpdateApplication({
			'event': "GetDeviceTypeHandler",
			'data': ans
		})

	def GetDeviceAdditionalHandler(self, data):
		ans = self.HW.GetDeviceAdditional(self.WorkingPort)
		print(ans)
		self.UpdateApplication({
			'event': "GetDeviceAdditionalHandler",
			'data': ans
		})

	def SetNodeAddressHandler(self, data):
		if len(data) > 0:
			address = int(data[0])
			ans = self.HW.SetNodeAddress(self.WorkingPort, address)
			print(ans)
			self.UpdateApplication({
				'event': "SetNodeAddressHandler",
				'data': ans
			})
		else:
			print("Wrong parameter")
	
	def GetNodeAddressHandler(self, data):
		ans = self.HW.GetNodeAddress(self.WorkingPort)
		print(ans)
		self.UpdateApplication({
			'event': "GetNodeAddressHandler",
			'data': ans
		})

	def GetNodeInfoHandler(self, data):
		ans = self.HW.GetNodeInfo(self.WorkingPort)
		print(ans)
		self.UpdateApplication({
			'event': "GetNodeInfoHandler",
			'data': ans
		})
	
	def GetNodeListHandler(self, data):
		ans = self.HW.GetNodeList(self.WorkingPort)
		print(ans)
		self.UpdateApplication({
			'event': "GetNodeListHandler",
			'data': ans
		})
	
	def GetNodesMapHandler(self, data):
		ans = (self.HW.GetNodesMap(self.WorkingPort))
		print(ans)
		self.UpdateApplication({
			'event': "GetNodesMapHandler",
			'data': ans
		})
	
	def AddNodeIndexHandler(self, data):
		if len(data) > 0:
			index = int(data[0])
			ans = self.HW.AddNodeIndex(self.WorkingPort, index)
			print(ans)
			self.UpdateApplication({
				'event': "AddNodeIndexHandler",
				'data': ans
			})
		else:
			print("Wrong parameter")
	
	def DelNodeIndexHandler(self, data):
		if len(data) > 0:
			index = int(data[0])
			ans = self.HW.DelNodeIndex(self.WorkingPort, index)
			print(ans)
			self.UpdateApplication({
				'event': "DelNodeIndexHandler",
				'data': ans
			})
		else:
			print("Wrong parameter")
	
	def SetRemoteWorkingNodeIdHandler(self, data):
		if len(data) > 0:
			self.RemoteNodeId = int(data[0])
		else:
			print("Wrong parameter")
	
	def GetRemoteNodeInfoHandler(self, data):
		ans = self.HW.GetRemoteNodeInfo(self.WorkingPort, self.RemoteNodeId)
		if ans is not None:
			info = self.Translator.Translate(ans["packet"])
			print(info)
			self.UpdateApplication({
				'event': "GetRemoteNodeInfoHandler",
				'data': info
			})

	def GetRemoteNodeDataHandler(self, data):
		if len(data) > 0:
			index = int(data[0])
			ans = self.HW.GetRemoteNodeData(self.WorkingPort, self.RemoteNodeId, index)
			if ans is not None:
				info = self.Translator.Translate(ans["packet"])
				print(info)
				self.UpdateApplication({
					'event': "GetRemoteNodeDataHandler",
					'data': info
				})
		else:
			print("Wrong parameter")
	
	def SetRemoteNodeDataHandler(self, data):
		if len(data) > 1:
			index = int(data[0])
			value = int(data[1])
			ans = self.HW.SetRemoteNodeData(self.WorkingPort, self.RemoteNodeId, index, value)
			if ans is not None:
				info = self.Translator.Translate(ans["packet"])
				print(info)
				self.UpdateApplication({
					'event': "SetRemoteNodeDataHandler",
					'data': info
				})
		else:
			print("Wrong parameter")
	
	def SetRemoteNodeAddressHandler(self, data):
		if len(data) > 0:
			address = int(data[0])
			ans = self.HW.SetRemoteNodeAddress(self.WorkingPort, self.RemoteNodeId, address)
			print(ans)
			self.UpdateApplication({
				'event': "SetRemoteNodeAddressHandler",
				'data': ans
			})
		else:
			print("Wrong parameter")
	
	def GetRemoteNodeAddressHandler(self, data):
		ans = self.HW.GetRemoteNodeAddress(self.WorkingPort, self.RemoteNodeId)
		print(ans)
		self.UpdateApplication({
			'event': "GetRemoteNodeAddressHandler",
			'data': ans
		})
	
	def UndefinedHandler(self, data):
		pass

	def AsyncDataArrived(self, port, packet):
		print("Terminal", packet)

	def Close(self):
		self.HW.Disconnect()
