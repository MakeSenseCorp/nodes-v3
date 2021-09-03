function Pidaptor(api) {
    var self = this;
    this.API = api;

    return this;
}
Pidaptor.prototype.GetGatwayInfo = function(callback) {
    this.API.SendCustomCommand("gateway_info", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetSystemInfo = function() {
    this.API.SendCustomCommand("system_info", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetSerialList = function(callback) {
    this.API.SendCustomCommand("list", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.Connect = function(port, baudrate) {
    this.API.SendCustomCommand("connect", {
        "async": false,
        "port": port,
        "baudrate": baudrate
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.Disconnect = function(port, baudrate) {
    this.API.SendCustomCommand("disconnect", {
        "async": false,
        "port": port
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetWorkingPort = function(port) {
    this.API.SendCustomCommand("setworkingport", {
        "async": false,
        "port": port
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.ListNodes = function() {
    this.API.SendCustomCommand("listnodes", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodeInfoRemote = function(node_id) {
    this.API.SendCustomCommand("getnodeinfo_r", {
        "async": false,
        "node_id": node_id
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetSensorDataRemote = function(node_id, sensor_index) {
    this.API.SendCustomCommand("getnodedata_r", {
        "async": false,
        "node_id": node_id,
        "sensor_index": sensor_index
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetSensorDataRemote = function(node_id, sensor_index, sensor_value) {
    this.API.SendCustomCommand("setnodedata_r", {
        "async": false,
        "node_id": node_id,
        "sensor_index": sensor_index,
        "sensor_value": sensor_value
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetDeviceType = function() {
    this.API.SendCustomCommand("getdevicetype", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetDeviceAdditional = function() {
    this.API.SendCustomCommand("getdeviceadditional", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetNodeAddress = function(address) {
    this.API.SendCustomCommand("setnodeaddress", {
        "async": false,
        "address": address
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodeAddress = function() {
    this.API.SendCustomCommand("getnodeaddress", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodeInfo = function() {
    this.API.SendCustomCommand("getnodeinfo", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodesMap = function() {
    this.API.SendCustomCommand("getnodesmap", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.AddNodeIndexHandler = function(index) {
    this.API.SendCustomCommand("addnodeindex", {
        "async": false,
        "index": index
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.DelNodeIndexHandler = function(index) {
    this.API.SendCustomCommand("delnodeindex", {
        "async": false,
        "index": index
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetRemoteNodeAddress = function(node_id, address) {
    this.API.SendCustomCommand("setnodeaddress_r", {
        "async": false,
        "node_id": node_id,
        "address": address
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetRemoteNodeAddress = function(node_id) {
    this.API.SendCustomCommand("getnodeaddress_r", {
        "async": false,
        "node_id": node_id
    }, function(data, error) {
        callback(data, error);
    });
}