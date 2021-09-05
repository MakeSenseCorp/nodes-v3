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
Pidaptor.prototype.GetSystemInfo = function(callback) {
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
Pidaptor.prototype.Connect = function(port, baudrate, callback) {
    this.API.SendCustomCommand("connect", {
        "async": false,
        "port": port,
        "baudrate": baudrate
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.Disconnect = function(port, callback) {
    this.API.SendCustomCommand("disconnect", {
        "async": false,
        "port": port
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetWorkingPort = function(port, callback) {
    this.API.SendCustomCommand("setworkingport", {
        "async": false,
        "port": port
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.ListNodes = function(callback) {
    this.API.SendCustomCommand("listnodes", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodeInfoRemote = function(node_id, callback) {
    this.API.SendCustomCommand("getnodeinfo_r", {
        "async": false,
        "node_id": node_id
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetSensorDataRemote = function(node_id, sensor_index, callback) {
    this.API.SendCustomCommand("getnodedata_r", {
        "async": false,
        "node_id": node_id,
        "sensor_index": sensor_index
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetSensorDataRemote = function(node_id, sensor_index, sensor_value, callback) {
    this.API.SendCustomCommand("setnodedata_r", {
        "async": false,
        "node_id": node_id,
        "sensor_index": sensor_index,
        "sensor_value": sensor_value
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetDeviceType = function(callback) {
    this.API.SendCustomCommand("getdevicetype", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetDeviceAdditional = function(callback) {
    this.API.SendCustomCommand("getdeviceadditional", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetNodeAddress = function(address, callback) {
    this.API.SendCustomCommand("setnodeaddress", {
        "async": false,
        "address": address
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodeAddress = function(callback) {
    this.API.SendCustomCommand("getnodeaddress", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodeInfo = function(callback) {
    this.API.SendCustomCommand("getnodeinfo", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetNodesMap = function(callback) {
    this.API.SendCustomCommand("getnodesmap", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.AddNodeIndexHandler = function(index, callback) {
    this.API.SendCustomCommand("addnodeindex", {
        "async": false,
        "index": index
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.DelNodeIndexHandler = function(index, callback) {
    this.API.SendCustomCommand("delnodeindex", {
        "async": false,
        "index": index
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SetRemoteNodeAddress = function(node_id, address, callback) {
    this.API.SendCustomCommand("setnodeaddress_r", {
        "async": false,
        "node_id": node_id,
        "address": address
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.GetRemoteNodeAddress = function(node_id, callback) {
    this.API.SendCustomCommand("getnodeaddress_r", {
        "async": false,
        "node_id": node_id
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.InsertDevice = function(device_type, device_id, callback) {
    this.API.SendCustomCommand("insert_device", {
        "async": false,
        "device_type": device_type,
        "device_id": device_id
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.DeleteDevice = function(device_id, callback) {
    this.API.SendCustomCommand("delete_device", {
        "async": false,
        "device_id": device_id
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SelectSensors = function(callback) {
    this.API.SendCustomCommand("select_sensors", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SelectDevices = function(callback) {
    this.API.SendCustomCommand("select_devices", {
        "async": false
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.UpdateSensorInfo = function(sensor_id, sensor_name, sensor_description, callback) {
    this.API.SendCustomCommand("update_sensor_info", {
        "async": false,
        "sensor_id": sensor_id,
        "sensor_name": sensor_name,
        "sensor_description": sensor_description
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SelectSensorsByDevice = function(device_id, callback) {
    this.API.SendCustomCommand("select_sensors_by_device", {
        "async": false,
        "device_id": device_id
    }, function(data, error) {
        callback(data, error);
    });
}
Pidaptor.prototype.SelectSensorHistory = function(sensor_id, callback) {
    this.API.SendCustomCommand("select_sensor_history", {
        "async": false,
        "sensor_id": sensor_id
    }, function(data, error) {
        callback(data, error);
    });
}