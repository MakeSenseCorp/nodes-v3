function MkSAPI () {
	self 		= this;
	this.WS 	= null;

	this.ModulesLoadedCallback = null;
	this.OnNodeChangeCallback = null;
	this.OnWSErrorCallback = null;
	this.OnWSCloseCallback = null;

	// Monitoring
	this.CallbacksMonitorId	= 0;

	// Callback management
	this.Callbacks 			= {};
	this.PacketCounter		= 1;
	this.SentPackets 		= [];

	window.ApplicationModules = {
		'Count': 0,
		'ModulesPathList': []
	}
	
	return this;
}

MkSAPI.prototype.ConvertHEXtoString = function(hexx) {
	var hex = hexx.toString();//force conversion
	var str = '';
	for (var i = 0; (i < hex.length && hex.substr(i, 2) !== '00'); i += 2) {
		str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
	}
	return str;
}

MkSAPI.prototype.ExecuteJS = function(content) {
	var oScript 	= document.createElement("script");
	var oScriptText = document.createTextNode(content);
	oScript.appendChild(oScriptText);
	document.body.appendChild(oScript);
}

MkSAPI.prototype.AppendCSS = function(content) {
	var styleSheet = document.createElement("style");
	styleSheet.type = "text/css";
	styleSheet.innerText = content;
	document.head.appendChild(styleSheet);
}

MkSAPI.prototype.ConnectLocalWS = function (ip, port, callback) {
	var self = this;
	var url	= "ws://" + ip;
	url = url.concat(":", port);

	console.log("LOCAL WEBSOCKET", url);

	this.WS = new WebSocket(url);
	this.WS.onopen = function () {
		console.log("LOCAL WEBSOCKET > CREATED", url);
		callback();
	};
	this.WS.onmessage = function (event) {
		var jsonData = JSON.parse(event.data);
		// console.log("LOCAL WEBSOCKET > DATA", jsonData);
		var identifier = jsonData.header.identifier;
		if (self.Callbacks[identifier]) {
			handler = self.Callbacks[identifier];
			if (handler.callback !== undefined && handler.callback !== null) {
				handler.callback(jsonData, {error: "none"});
			}

			// console.log("[LOCAL #2] Delete Identifier #", identifier);	
			delete self.Callbacks[identifier];
		} else {
			if (identifier == -1) {
				if (null != self.OnNodeChangeCallback) {
					self.OnNodeChangeCallback(jsonData);
				}
			} else {
			}
		}
	}
	this.WS.onerror = function (event) {
		console.log("[ERROR] Websocket", event.data);
		if (null != self.OnWSErrorCallback) {
			self.OnWSErrorCallback(event.data);
		}
	}
	this.WS.onclose = function () {
		console.log("[LOCAL WEBSOCKET] Connection closed...");
		if (null != self.OnWSCloseCallback) {
			self.OnWSCloseCallback(event.data);
		}
	};
}

MkSAPI.prototype.DisconnectLocalWS = function (ip, port, callback) {
	this.WS.close();
}

MkSAPI.prototype.CallbacksMonitor = function () {
	// console.log("(CallbacksMonitor)");
	if (0 == Object.keys(this.Callbacks).length) {
		//console.log("(CallbacksMonitor) Callbacks list empty");
		clearInterval(this.CallbacksMonitorId);
		this.CallbacksMonitorId	= 0;
	} else {
		for (key in this.Callbacks) {
			if (this.Callbacks.hasOwnProperty(key)) {
				item = this.Callbacks[key];
				
				if (item.timeout_counter > item.timeout) {
					try {
						if (item.callback !== undefined && item.callback !== null) {
							item.callback(null, {error: "timeout"});
						}
					}
					catch (e) {
						console.log("[ERROR] (CallbacksMonitor)", e.message);
					}
					
					delete this.Callbacks[key];
					// console.log(Object.keys(this.Callbacks).length);
				} else {
					item.timeout_counter++;
					// console.log(item.timeout_counter, item.timeout);
				}
			}
		}
	}
}

MkSAPI.prototype.SendPacket = function (cmd, payload, callback) {
	if ("" == payload) {
		payload = {};
	}

	request = {
		header: {
			command: cmd,
			timestamp: Date.now(),
			identifier: this.PacketCounter
		},
		payload: payload
	}

	this.Callbacks[this.PacketCounter] = { 
		callback: callback,
		timeout_counter: 0,
		timeout: 10
		};

	this.PacketCounter++;
	if (this.PacketCounter < 1) {
		this.PacketCounter = 0;
	}

	this.WS.send(JSON.stringify(request));

	if (!this.CallbacksMonitorId) {
		this.CallbacksMonitorId = setInterval(this.CallbacksMonitor.bind(this), 1000);
	}
}

MkSAPI.prototype.GetFileContent = function (payload, callback) {
	this.SendPacket("get_file", payload, callback);
}

MkSAPI.prototype.UploadFileContent = function (payload, callback) {
	this.SendPacket("upload_file", payload, callback);
}

MkSAPI.prototype.SendCustomCommand = function (command, payload, callback) {
	this.SendPacket(command, payload, callback);
}

MkSAPI.prototype.RegisterOnNodeChange = function (callback) {
	this.SendPacket("register_on_node_change", {}, callback);
}

MkSAPI.prototype.UnregisterOnNodeChange = function (callback) {
	this.SendPacket("unregister_on_node_change", {}, callback);
}

MkSAPI.prototype.AppendModule = function(name) {
	window.ApplicationModules.ModulesPathList.push(name+".js");
	window.ApplicationModules.Count++;
}

MkSAPI.prototype.GetModules = function(name) {
	for (key in window.ApplicationModules.ModulesPathList) {
		this.LoadModule(window.ApplicationModules.ModulesPathList[key]);
	}
}

MkSAPI.prototype.LoadModule = function(name) {
	var self = this;
	this.GetFileContent({
		"file_path": "modules/"+name
	}, function(res) {
		var payload = res.payload;
		var js = self.ConvertHEXtoString(payload.content);
		// Inject into DOM
		self.ExecuteJS(js);
		window.ApplicationModules.Count--;
		console.log(window.ApplicationModules.Count);
		if (window.ApplicationModules.Count == 0) {
			if (self.ModulesLoadedCallback != null) {
				self.ModulesLoadedCallback();
			}
		}
	});
}	

var MkSAPIBuilder = (function () {
	var Instance;

	function CreateInstance () {
		return new MkSAPI();
	}

	return {
		GetInstance: function () {
			if (!Instance) {
				console.log("Create API instance");
				Instance = CreateInstance();
			}

			console.log("Return API instance");
			return Instance;
		}
	};
})();
