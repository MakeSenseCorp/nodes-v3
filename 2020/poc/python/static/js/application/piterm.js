function Piterm(api) {
    var self = this;
    this.API = api;

    return this;
}
Piterm.prototype.GetGatwayInfo = function() {
    this.API.SendCustomCommand("gateway_info", {
        "async": true
    }, null);
}
Piterm.prototype.GetSystemInfo = function() {
    this.API.SendCustomCommand("system_info", {
        "async": true
    }, null);
}
Piterm.prototype.GetSerialList = function() {
    this.API.SendCustomCommand("list", {
        "async": true
    }, null);
}
Piterm.prototype.Connect = function(port, baudrate) {
    this.API.SendCustomCommand("connect", {
        "async": true,
        "port": port,
        "baudrate": baudrate
    }, null);
}
Piterm.prototype.Disconnect = function(port, baudrate) {
    this.API.SendCustomCommand("disconnect", {
        "async": true,
        "port": port
    }, null);
}
Piterm.prototype.SetWorkingPort = function(port) {
    this.API.SendCustomCommand("setworkingport", {
        "async": true,
        "port": port
    }, null);
}
Piterm.prototype.GetListNodes = function() {
    this.API.SendCustomCommand("listnodes", {
        "async": true
    }, null);
}
Piterm.prototype.GetNodeInfoRemote = function(node_id) {
    this.API.SendCustomCommand("getnodeinfo_r", {
        "async": true,
        "node_id": node_id
    }, null);
}
Piterm.prototype.GetSensorDataRemote = function(node_id, sensor_index) {
    this.API.SendCustomCommand("getnodedata_r", {
        "async": true,
        "node_id": node_id,
        "sensor_index": sensor_index
    }, null);
}
Piterm.prototype.SetSensorDataRemote = function(node_id, sensor_index, sensor_value) {
    this.API.SendCustomCommand("setnodedata_r", {
        "async": true,
        "node_id": node_id,
        "sensor_index": sensor_index,
        "sensor_value": sensor_value
    }, null);
}
Piterm.prototype.GetDeviceType = function() {
    this.API.SendCustomCommand("getdevicetype", {
        "async": true
    }, null);
}
Piterm.prototype.GetDeviceAdditional = function() {
    this.API.SendCustomCommand("getdeviceadditional", {
        "async": true
    }, null);
}
Piterm.prototype.SetNodeAddress = function(address) {
    this.API.SendCustomCommand("setnodeaddress", {
        "async": true,
        "address": address
    }, null);
}
Piterm.prototype.GetNodeAddress = function() {
    this.API.SendCustomCommand("getnodeaddress", {
        "async": true
    }, null);
}
Piterm.prototype.GetNodeInfo = function() {
    this.API.SendCustomCommand("getnodeinfo", {
        "async": true
    }, null);
}
Piterm.prototype.GetNodesMap = function() {
    this.API.SendCustomCommand("getnodesmap", {
        "async": true
    }, null);
}
Piterm.prototype.AddNodeIndexHandler = function(index) {
    this.API.SendCustomCommand("addnodeindex", {
        "async": true,
        "index": index
    }, null);
}
Piterm.prototype.DelNodeIndexHandler = function(index) {
    this.API.SendCustomCommand("delnodeindex", {
        "async": true,
        "index": index
    }, null);
}
Piterm.prototype.SetRemoteNodeAddress = function(node_id, address) {
    this.API.SendCustomCommand("setnodeaddress_r", {
        "async": true,
        "node_id": node_id,
        "address": address
    }, null);
}
Piterm.prototype.GetRemoteNodeAddress = function(node_id) {
    this.API.SendCustomCommand("getnodeaddress_r", {
        "async": true,
        "node_id": node_id
    }, null);
}
Piterm.prototype.InsertDevice = function(device_type, device_id) {
    this.API.SendCustomCommand("insert_device", {
        "async": true,
        "device_type": device_type,
        "device_id": device_id
    }, null);
}
Piterm.prototype.DeleteDevice = function(device_id) {
    this.API.SendCustomCommand("delete_device", {
        "async": true,
        "device_id": device_id
    }, null);
}
Piterm.prototype.SelectSensors = function() {
    this.API.SendCustomCommand("select_sensors", {
        "async": true
    }, null);
}
Piterm.prototype.SelectDevices = function() {
    this.API.SendCustomCommand("select_devices", {
        "async": true
    }, null);
}
Piterm.prototype.UpdateSensorInfo = function(sensor_id, sensor_name, sensor_description) {
    this.API.SendCustomCommand("update_sensor_info", {
        "async": true,
        "sensor_id": sensor_id,
        "sensor_name": sensor_name,
        "sensor_description": sensor_description
    }, null);
}
Piterm.prototype.SelectSensorsByDevice = function(device_id) {
    this.API.SendCustomCommand("select_sensors_by_device", {
        "async": true,
        "device_id": device_id
    }, null);
}
Piterm.prototype.SelectSensorHistory = function(sensor_id) {
    this.API.SendCustomCommand("select_sensor_history", {
        "async": true,
        "sensor_id": sensor_id
    }, null);
}