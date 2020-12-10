import websocket
try:
	import thread
except ImportError:
	import _thread as thread
import time
import signal

'''
def on_message(ws, message):
	print(message)

def on_error(ws, error):
	print(error)

def on_close(ws):
	print("### closed ###")

def on_open(ws):
	def run(*args):
		for i in range(3):
			time.sleep(1)
			ws.send("Hello %d" % i)
		time.sleep(1)
		ws.close()
		print("thread terminating...")
	thread.start_new_thread(run, ())


if __name__ == "__main__":
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://10.0.2.15:1981/",
				on_message = on_message,
				on_error = on_error,
				on_close = on_close)
	ws.header	= 	{
						'uuid':'12345678-1234-1234-1234-123456789100', 
						'node_type':'1', 
						'payload': '{"node_name": "Master", "node_type": 1}', 
						'key':'ac6de837-7863-72a9-c789-a0aae7e9d93e'
					}
	#{'payload': '{"node_name": "Master", "node_type": 1}', 'key': 'ac6de837-7863-72a9-c789-a0aae7e9d93e', 'node_type': '1', 'uuid': '12345678-1234-1234-1234-123456789100'}
	ws.on_open = on_open
	ws.run_forever()
'''

'''
class WSock ():
	def __init__(self, uri):
		self.URI = uri
		self.wss = None
		self.Run = True
		self.WS  = None
	
	def OnGatewayOpenEvent(self):
		print("OnGatewayOpenEvent")

	def OnGatewayMessageArrivedEvent(self, data):
		print(data)

	def OnGatewayCloseEvent(self):
		print("OnGatewayCloseEvent")

	def OnGatewayErrorEvent(self, error):
		print(error)

websocket.enableTrace(True)
Gateway = WSock("ws://10.0.2.15:1981/")

def gateway_on_message(ws, message):
	Gateway.OnGatewayMessageArrivedEvent(message)

def gateway_on_error(ws, error):
	Gateway.OnGatewayErrorEvent(error)

def gateway_on_close(ws):
	Gateway.OnGatewayCloseEvent()

def gateway_on_open(ws):
	Gateway.OnGatewayOpenEvent()

def signal_handler(signal, frame):
	global Gateway
	Gateway.Run = False

def WebsocketWorker():
	global Gateway
	Gateway.WS = websocket.WebSocketApp("ws://10.0.2.15:1981/",
				on_message = gateway_on_message,
				on_error = gateway_on_error,
				on_close = gateway_on_close)
	Gateway.WS.header = {
		'uuid':'12345678-1234-1234-1234-123456789100', 
		'node_type':'1', 
		'payload': '{"node_name": "Master", "node_type": 1}', 
		'key':'ac6de837-7863-72a9-c789-a0aae7e9d93e'
	}
	Gateway.WS.on_open = gateway_on_open
	Gateway.WS.run_forever()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)	
	thread.start_new_thread(WebsocketWorker, ())
	while (Gateway.Run is True):
		if Gateway.WS is not None:
			Gateway.WS.send("Hello")
		time.sleep(1)
'''

class WSock ():
	def __init__(self, uri):
		self.URI = uri
		self.wss = None
		self.Run = True
		self.WS  = None
	
	def OnGatewayOpenEvent(self):
		print("OnGatewayOpenEvent")

	def OnGatewayMessageArrivedEvent(self, data):
		print(data)

	def OnGatewayCloseEvent(self):
		print("OnGatewayCloseEvent")

	def OnGatewayErrorEvent(self, error):
		print(error)

	def gateway_on_message(self, ws, message):
		self.OnGatewayMessageArrivedEvent(message)

	def gateway_on_error(self, ws, error):
		self.OnGatewayErrorEvent(error)

	def gateway_on_close(self, ws):
		self.OnGatewayCloseEvent()

	def gateway_on_open(self, ws):
		self.OnGatewayOpenEvent()

	def WebsocketWorker(self):
		websocket.enableTrace(True)
		self.WS = websocket.WebSocketApp("ws://10.0.2.15:1981/",
					on_message = self.gateway_on_message,
					on_error = self.gateway_on_error,
					on_close = self.gateway_on_close)
		self.WS.header = {
			'uuid':'12345678-1234-1234-1234-123456789100', 
			'node_type':'1', 
			'payload': '{"node_name": "Master", "node_type": 1}', 
			'key':'ac6de837-7863-72a9-c789-a0aae7e9d93e'
		}
		self.WS.on_open = self.gateway_on_open
		self.WS.run_forever()
	
	def Start(self):
		self.Run = True
		thread.start_new_thread(self.WebsocketWorker, ())
	
	def Stop(self):
		self.Run = False
	
	def Send(self, data):
		if self.WS is not None:
			self.WS.send("Hello")

AppRunning = True
def signal_handler(signal, frame):
	global AppRunning
	AppRunning = False

if __name__ == "__main__":
	global AppRunning
	signal.signal(signal.SIGINT, signal_handler)	
	Gateway = WSock("ws://10.0.2.15:1981/")
	Gateway.Start()
	while (AppRunning is True):
		Gateway.Send("Hello")
		time.sleep(1)
	Gateway.Stop()
