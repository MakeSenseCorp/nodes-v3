function Application() {
    var self = this;
    // Get makesense api instanse.
    this.API = MkSAPIBuilder.GetInstance();
    // Default handler
    this.API.OnUnexpectedDataArrived = function (packet) {
        console.log(packet);
    }
    this.API.ModulesLoadedCallback = function () {
        self.NodeLoaded();
    }
    this.EventMapper = {};
    this.Adaptor = new Pidaptor(this.API);
    this.Terminal = new Piterm(this.API);

    this.Devices            = {};
    this.Sensors            = {};
    this.GatewayOnline      = false;
    this.DefaultGateway     = null;
    this.System             = null;

    return this;
}
Application.prototype.RegisterEventHandler = function(name, callback, scope) {
    this.EventMapper[name] = { 
        callback: callback,
        scope: scope
    };
}
Application.prototype.UnregisterEventHandler = function(name) {
    delete this.EventMapper[name];
}
Application.prototype.Publish = function(name, data) {
    var handler  = this.EventMapper[name];
    if (handler !== undefined && handler !== null) {
        handler.callback(data, handler.scope);
    }
}
Application.prototype.Connect = function(ip, port, callback) {
    var self = this;
    console.log("Connect Application");
    // Python will emit messages
    self.API.OnNodeChangeCallback = self.OnChangeEvent.bind(self);
    this.API.ConnectLocalWS(ip, port, function() {
        console.log("Connected to local websocket");

        // Module area
        self.API.GetModules();

        callback();
    });
}
Application.prototype.NodeLoaded = function () {
    console.log("Modules Loaded");

}
Application.prototype.OnChangeEvent = function(packet) {
    var event = packet.payload.event;
    var data = packet.payload.data;
    this.Publish(event, data);
}
// ASYNC REGISTERED HANDLERS
Application.prototype.SystemInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SerialListHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodeListHandler = function(data, scope) {
    console.log("GetNodeListHandler", data);
    if (data === undefined || data === null) {
        return;
    }

    app.UpdateListViewDevices(data);
}
Application.prototype.GetRemoteNodeInfoHandler = function(data, scope) {
    // TODO - Update sensors value
    console.log("GetRemoteNodeInfoHandler", data);
}
Application.prototype.GetRemoteNodeDataHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SetRemoteNodeDataHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetDeviceTypeHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetDeviceAdditionalHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SetNodeAddressHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodeAddressHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodeInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodesMapHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.AddNodeIndexHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DelNodeIndexHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SetRemoteNodeAddressHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DelNodeIndexHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.USBDeviceConnectedHandler = function(data, scope) {
    // TODO - Update UI USB device
    console.log("USBDeviceConnectedHandler", data);
    scope.LoadSystem(function() {

    });
}
Application.prototype.USBDeviceDisconnectedHandler = function(data, scope) {
    // TODO - Update UI USB device
    console.log("USBDeviceDisconnectedHandler", data);
    scope.LoadSystem(function() {

    });
}
Application.prototype.SetWorkingPortHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GatewayInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.NRFPacket = function(data, scope) {
    // TODO - Update sensors value
    console.log("NRFPacket", data);
    app.UpdateListViewSensors(data);
}
Application.prototype.InsertDeviceHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SelectSensorsHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DeleteDeviceHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SelectDevicesHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.UpdateSensorInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DeviceCommunicationLostHandler = function(data, scope) {
    // TODO - Update UI device communication lost
    console.log("DeviceCommunicationLostHandler", data);
    this.GetHWDevices(function(obj) {

    });
}
Application.prototype.SelectSensorsByDeviceHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SelectSensorHistoryHandler = function(data, scope) {
    console.log(data);
}

Application.prototype.SetDefaultGatewayWorkingPort = function(callback) {
    if (this.GatewayOnline == true) {
        app.Adaptor.SetWorkingPort(this.DefaultGateway.port, function(data, error) {
            if (callback !== undefined && callback != null) {
                callback(true);
            }
        });
    } else {
        if (callback !== undefined && callback != null) {
            callback(false);
        }
    }
}
Application.prototype.GetSystem = function(callback) {
    var self = this;
    this.GatewayOnline  = false;
    this.DefaultGateway = null;
    this.System         = null;

    console.log("GetSystem");
    app.Adaptor.GetSystemInfo(function(data, error) {
        self.System = data.payload.system;
        var gateways = self.System.local_db.gateways;

        console.log("GetSystemInfo", self.System);
        if (Object.keys(gateways).length == 0) {
            self.GatewayOnline = false;
            if (callback !== undefined && callback != null) {
                callback(false);
            }
            return;
        }
        self.GatewayOnline = true;
        self.DefaultGateway = self.System.local_db.gateways[Object.keys(self.System.local_db.gateways)[0]];
        console.log("Set Default Gateway");

        if (callback !== undefined && callback != null) {
            callback(true);
        }
    });
}
Application.prototype.GetDataBaseDevices = function(callback) {
    var self = this;

    app.Adaptor.SelectDevices(function(data, error) {
        console.log("SelectDevices", data.payload);
        var device_list_obj = document.getElementById("id_app_mobile_device_list");
        var ul_item = `
            <li>
                <a href="#">
                    <span data-feather="hard-drive"></span>
                    <h2>Device (THMR)</h2>
                    <p class="ui-li-aside" id="id_app_mobile_device_list_[ID]">Unknown</p>
                </a>
                <a href="#purchase" data-rel="popup" data-position-to="window" data-transition="pop">Purchase album</a>
            </li>
        `;
        var injected_html = "";

        for (idx in data.payload) {
            var device = data.payload[idx];
            device.connected = false;
            self.Devices[device.device_id] = device;
            injected_html += ul_item.split("[ID]").join(device.device_id);
        }

        device_list_obj.innerHTML = injected_html;
        $("#id_app_mobile_device_list").listview("refresh");

        // Call callback
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}
Application.prototype.GetDataBaseSensors = function(callback) {
    var self = this;

    app.Adaptor.SelectSensors(function(data, error) {
        console.log("GetDataBaseSensors", data.payload);
        var sensor_list_obj = document.getElementById("id_app_mobile_sensor_list");
        var div_item = `
            <div class="ui-block-[INDEX]" onclick="app.SensorOnClickEvent([DEVICE_ID],[SENSOR_INDEX])">
                <div class="ui-bar ui-bar-a" style="height:60px">
                    <ul data-role="listview">
                        <li data-icon="star">
                            <a href="#">
                                <h2 id="id_app_mobile_sensor_[DEVICE_ID]_[SENSOR_INDEX]"><span data-feather="[SENSOR_ICON]"></span>[VALUE]</h2>
                                <p>[NAME]</p>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        `;
        var injected_html = "";
        var block_map = {
            0: "a",
            1: "b",
            2: "c"
        }
        var sensor_icon_map = {
            1: "thermometer",
            2: "cloud-rain",
            3: "user",
            4: "sun"
        }
        var modulo = 0;

        for (idx in data.payload) {
            var html = div_item;
            var sensor = data.payload[idx];
            sensor.value = 0;
            self.Sensors[[sensor.device_id, sensor.index]] = sensor;

            modulo = idx % 3;

            html = html.split("[INDEX]").join(block_map[modulo]);
            html = html.split("[SENSOR_ICON]").join(sensor_icon_map[sensor.type]);
            html = html.split("[DEVICE_ID]").join(sensor.device_id);
            html = html.split("[SENSOR_INDEX]").join(sensor.index);
            html = html.split("[VALUE]").join("");
            html = html.split("[NAME]").join(sensor.name);
            injected_html += html;
        }

        sensor_list_obj.innerHTML = injected_html;

        $('#id_app_mobile_sensor_list ul').each(function() {
            $(this).listview().listview("refresh");
        })
        feather.replace();

        // Call callback
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}
Application.prototype.SensorOnClickEvent = function(device_id, sensor_index) {
    if (app.Sensors.hasOwnProperty([device_id, sensor_index]) == true) {
        var sensor = app.Sensors[[device_id, sensor_index]];
        if (sensor.type == 4) {
            var value = 0;
            if (sensor.value == 0) {
                value = 1;
            }

            app.Adaptor.SetSensorDataRemote(device_id, sensor_index, value, function(data, error) {
                console.log("SetSensorDataRemote", data);
            });
        }
    }
}
Application.prototype.UpdateListViewSensors = function(data) {
    console.log("UpdateListViewSensors", data);
    var sensor_icon_map = {
        1: "thermometer",
        2: "cloud-rain",
        3: "user",
        4: "sun"
    }
    if (data.sensors.length > 0) {
        // TODO - Update device status
        for (idx in data.sensors) {
            var sensor = data.sensors[idx];
            if (app.Sensors.hasOwnProperty([data.device_id, sensor.index]) == true) {
                app.Sensors[[data.device_id, sensor.index]].value = sensor.value;

                html = `<span data-feather="[SENSOR_ICON]" style="color:[COLOR]"></span>[VALUE]`;
                html = html.split("[SENSOR_ICON]").join(sensor_icon_map[sensor.type]);

                if (sensor.type == 3 || sensor.type == 4) {
                    html = html.split("[VALUE]").join("");
                    if (sensor.value == 1) {
                        html = html.split("[COLOR]").join("red");
                    } else {
                        html = html.split("[COLOR]").join("black");
                    }
                } else {
                    html = html.split("[COLOR]").join("black");
                    html = html.split("[VALUE]").join("  "+sensor.value);
                }
                document.getElementById("id_app_mobile_sensor_"+data.device_id+"_"+sensor.index).innerHTML = html;
            }
        }
    } else {
        console.log("UpdateListViewSensors", "Empty", data.length);
    }
    feather.replace();
}
Application.prototype.UpdateListViewDevices = function(data) {
    console.log("UpdateListViewDevices", data);
    if (data.list.length > 0) {
        // TODO - Update device status
        for (idx in data.list) {
            var device = data.list[idx];
            if (app.Devices.hasOwnProperty(device.device_id) == true) {
                if (device.status == 1) {
                    app.Devices[device.device_id].connected = true;
                    document.getElementById("id_app_mobile_device_list_"+device.device_id).innerHTML = "Connected";
                } else {
                    app.Devices[device.device_id].connected = false;
                    document.getElementById("id_app_mobile_device_list_"+device.device_id).innerHTML = "Disconnected";
                }
            }
        }
    } else {
        console.log("Empty", data.list.length)
        for (key in app.Devices) {
            var device = app.Devices[key];
            device.connected = false;
            document.getElementById("id_app_mobile_device_list_"+device.device_id).innerHTML = "Disconnected";
        }
    }
}
Application.prototype.GetHWDevices = function(callback) {
    var self = this;

    app.Adaptor.ListNodes(function(data, error) {
        console.log("GetHWDevices", data.payload);
        self.UpdateListViewDevices(data.payload);

        // Call callback
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}
Application.prototype.LoadSystem = function(callback) {
    var self = this;
    this.GetSystem(function(status) {
        self.GetDataBaseDevices(function(obj) {
            self.SetDefaultGatewayWorkingPort(function(status) {
                self.GetHWDevices(function(obj) {
                    self.GetDataBaseSensors(function(obj) {

                    });
                    // Call callback
                    if (callback !== undefined && callback != null) {
                        callback();
                    }
                });
            });
        });
    });
}

var app = new Application();
app.RegisterEventHandler("SelectSensorHistoryHandler",      app.SelectSensorHistoryHandler,     app);
app.RegisterEventHandler("SelectSensorsByDeviceHandler",    app.SelectSensorsByDeviceHandler,   app);
app.RegisterEventHandler("DeviceCommunicationLostHandler",  app.DeviceCommunicationLostHandler, app);
app.RegisterEventHandler("UpdateSensorInfoHandler",         app.UpdateSensorInfoHandler,        app);
app.RegisterEventHandler("SelectDevicesHandler",            app.SelectDevicesHandler,           app);
app.RegisterEventHandler("DeleteDeviceHandler",             app.DeleteDeviceHandler,            app);
app.RegisterEventHandler("SelectSensorsHandler",            app.SelectSensorsHandler,           app);
app.RegisterEventHandler("InsertDeviceHandler",             app.InsertDeviceHandler,            app);
app.RegisterEventHandler("NRFPacket",                       app.NRFPacket,                      app);
app.RegisterEventHandler("SystemInfoHandler",               app.SystemInfoHandler,              app);
app.RegisterEventHandler("GatewayInfoHandler",              app.GatewayInfoHandler,             app);
app.RegisterEventHandler("SerialListHandler",               app.SerialListHandler,              app);
app.RegisterEventHandler("SetWorkingPortHandler",           app.SetWorkingPortHandler,          app);
app.RegisterEventHandler("GetNodeListHandler",              app.GetNodeListHandler,             app);
app.RegisterEventHandler("GetRemoteNodeInfoHandler",        app.GetRemoteNodeInfoHandler,       app);
app.RegisterEventHandler("GetRemoteNodeDataHandler",        app.GetRemoteNodeDataHandler,       app);
app.RegisterEventHandler("SetRemoteNodeDataHandler",        app.SetRemoteNodeDataHandler,       app);
app.RegisterEventHandler("GetDeviceTypeHandler",            app.GetDeviceTypeHandler,           app);
app.RegisterEventHandler("GetDeviceAdditionalHandler",      app.GetDeviceAdditionalHandler,     app);
app.RegisterEventHandler("SetNodeAddressHandler",           app.SetNodeAddressHandler,          app);
app.RegisterEventHandler("GetNodeAddressHandler",           app.GetNodeAddressHandler,          app);
app.RegisterEventHandler("GetNodeInfoHandler",              app.GetNodeInfoHandler,             app);
app.RegisterEventHandler("GetNodesMapHandler",              app.GetNodesMapHandler,             app);
app.RegisterEventHandler("AddNodeIndexHandler",             app.AddNodeIndexHandler,            app);
app.RegisterEventHandler("DelNodeIndexHandler",             app.DelNodeIndexHandler,            app);
app.RegisterEventHandler("SetRemoteNodeAddressHandler",     app.SetRemoteNodeAddressHandler,    app);
app.RegisterEventHandler("GetRemoteNodeAddressHandler",     app.GetRemoteNodeAddressHandler,    app);
app.RegisterEventHandler("USBDeviceConnectedHandler",       app.USBDeviceConnectedHandler,      app);
app.RegisterEventHandler("USBDeviceDisconnectedHandler",    app.USBDeviceDisconnectedHandler,   app);

app.Connect(global_ip, global_port, function() {
    app.LoadSystem(function() {

    });
});

feather.replace();