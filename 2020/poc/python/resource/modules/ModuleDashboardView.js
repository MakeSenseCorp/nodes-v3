function ModuleDashboardView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;

    this.GatewayOnline              = false;
    this.DefaultGateway             = null;
    this.USBDevices                 = {};
    this.Devices                    = {};
    this.Sensors                    = {};
    this.System                     = null;
    this.ModuleNodeViewObj          = null;
    this.ModuleGatewayViewObj       = null;

    return this;
}

ModuleDashboardView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleDashboardView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleDashboardView.prototype.Build = function(data, callback) {
    var self = this;

    app.API.GetFileContent({
        "file_path": "modules/ModuleDashboardView.html"
    }, function(res) {
        // Get payload
        var payload = res.payload;
        // Get HTML content
        self.HTML = app.API.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        // Each UI module have encapsulated conent in component object (DIV)
        self.ComponentObject = document.getElementById("id_m_component_view_"+this.HostingID);
        // Apply HTML to DOM
        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            self.HostingObject.innerHTML = self.HTML;
        }
        // Call callback
        if (callback !== undefined && callback != null) {
            callback(self);
        }

        self.LoadingProcess();
    });
}

ModuleDashboardView.prototype.Clean = function() {
    document.getElementById("id_m_usb_device_table").innerHTML = "";
    document.getElementById("id_m_sensors_table").innerHTML = "";
    document.getElementById("id_m_remote_device_table").innerHTML = "";

    this.USBDevices                 = {};
    this.Devices                    = {};
    this.Sensors                    = {};
    this.System                     = null;
}

ModuleDashboardView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleDashboardView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}

ModuleDashboardView.prototype.LoadSystem = function(callback) {
    var self = this;

    console.log("LoadSystem");
    app.Adaptor.GetSystemInfo(function(data, error) {
        var system = data.payload.system;
        self.System = system;
        var gateways = system.local_db.gateways;
        var nodes = system.local_db.nodes;
        console.log(nodes);

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

        for (key in gateways) {
            var gateway = gateways[key];
            if (self.USBDevices.hasOwnProperty(gateway.port) == false) {
                self.USBDevices[gateway.port] = {
                    "type": "GATEWAY",
                    "port": gateway.port,
                    "index": gateway.index
                };
            }
        }
        for (key in nodes) {
            var node = nodes[key];
            if (self.USBDevices.hasOwnProperty(node.port) == false) {
                self.USBDevices[node.port] = {
                    "type": "NODE",
                    "port": node.port,
                    "index": node.index
                };
            }
        }

        if (callback !== undefined && callback != null) {
            callback(true);
        }
    });
}

ModuleDashboardView.prototype.LoadDevices = function(callback) {
    var self = this;

    console.log("LoadDevices", this.GatewayOnline);
    if (this.GatewayOnline == false) {
        if (callback !== undefined && callback != null) {
            callback(false);
        }
        return;
    }

    app.Adaptor.SelectDevices(function(data, error) {
        devices = data.payload;
        for (key in devices) {
            var device = devices[key];
            if (self.Devices.hasOwnProperty(device.device_id) == false) {
                self.Devices[device.device_id] = {
                    "type": device.device_type,
                    "id": device.device_id,
                    "sensor_count": device.sensors_count,
                    "status": false,
                    "sensors": {}
                };
            }
        }

        var gateway = self.DefaultGateway;
        app.Adaptor.SetWorkingPort(gateway.port, function(data, error) {
            app.Adaptor.ListNodes(function(data, error) {
                var nodes = data.payload.list;
                for (key in nodes) {
                    var node = nodes[key];
                    if (self.Devices.hasOwnProperty(node.device_id) == false) {
                        app.Adaptor.DelNodeIndexHandler(node.device_id, function(data, error) {
                            console.log("Node deleted from gateway", data.payload.device_id);
                        });
                    } else {
                        self.Devices[node.device_id].status = node.status;
                    }
                }

                if (callback !== undefined && callback != null) {
                    callback(true);
                }
            });
        });
    });
}

ModuleDashboardView.prototype.LoadSensors = function(callback) {
    var self = this;

    console.log("LoadSensors");
    if (this.GatewayOnline == false) {
        if (callback !== undefined && callback != null) {
            callback(false);
        }
        return;
    }

    app.Adaptor.SelectSensors(function(data, error) {
        var sensors = data.payload;
        for (key in sensors) {
            var sensor = sensors[key];
            sensor.value = 0;
            self.Sensors[[sensor.device_id, sensor.index]] = sensor;
        }
        
        for (key in self.Devices) {
            var device = self.Devices[key];
            if (device.status == true) {
                app.Adaptor.GetNodeInfoRemote(device.id, function(data, error) {
                    self.NRFDataEvent(data.payload);
                    self.UpdateSensorsTable();
                });
            }
        }

        if (callback !== undefined && callback != null) {
            callback(true);
        }
    })
}

ModuleDashboardView.prototype.LoadingProcess = function() {
    var self = this;

    this.LoadSystem(function(status) {
        console.log("System Loaded");
        self.LoadDevices(function(status) {
            console.log("Devices Loaded");
            self.LoadSensors(function(status) {
                console.log("Sensors Loaded");
                self.UpdateUSBDevicesTable();
                self.UpdateDevicesTable();
                self.UpdateSensorsTable();
            });
        });
    });

    
}

ModuleDashboardView.prototype.UpdateUSBDevicesTable = function() {
    var self = this;

    console.log("UpdateUSBDevicesTable");

    var data = [];
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", "", "", ""]);
    for (key in this.USBDevices) {
        var device = this.USBDevices[key];
        row = [];
        row.push(`<h6 class="my-0"><a href="#" onclick="">`+device.type+`</a></h6>`);
        row.push(`<div>`+device.port+`</div>`);
        row.push(`<div>`+device.index+`</div>`);
        row.push(`<div><span style="color: green; cursor: pointer;">Connected</span></div>`);
        if (device.type == "NODE") {
            if (self.Devices.hasOwnProperty(device.index) == false) {
                row.push(`<span style="color: red;cursor: pointer;" onclick="window.ApplicationModules.DashboardView.AppendDeviceOnclickEvent(50,`+device.index+`);" data-feather="thumbs-down"></span>`);
            } else {
                row.push(`<span style="color: green;cursor: pointer;" onclick="" data-feather="thumbs-up"></span>`);
            }
        } else {
            row.push(``);
        }
        row.push(`<span style="color: green;cursor: pointer;" onclick="window.ApplicationModules.DashboardView.SettingsOnclickEvent('`+device.port+`');" data-feather="settings"></span>`);
        data.push(row);
    }
    table.ShowRowNumber(true);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_usb_device_table"));
    feather.replace();
}

ModuleDashboardView.prototype.UpdateDevicesTable = function() {
    var self = this;

    var data = [];
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", "", "", ""]);
    for (key in this.Devices) {
        var device = this.Devices[key];
        row = [];
        row.push(`<h6 class="my-0"><a href="#" onclick="">`+device.type+`</a></h6>`);
        row.push(`<div>`+device.id+`</div>`);
        row.push(`<div>`+device.sensor_count+`</div>`);
        if (device.status == true) {
            row.push(`<div><strong><span style="color: green; cursor: pointer;">Online</span></strong></div>`);
        } else {
            row.push(`<div><strong><span style="color: red; cursor: pointer;">Offline</span></strong></div>`);
        }
        row.push(`<span style="color: gray;cursor: pointer;" onclick="" data-feather="settings"></span>`);
        row.push(`<span style="color: red;cursor: pointer;" onclick="window.ApplicationModules.DashboardView.DeleteDeviceOnclickEvent(`+device.id+`);" data-feather="delete"></span>`);
        data.push(row);
    }
    table.ShowRowNumber(true);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_remote_device_table"));
    feather.replace();
}

ModuleDashboardView.prototype.UpdateSensorsTable = function() {
    var self = this;

    var data = [];
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", "", ""]);
    for (key in this.Sensors) {
        var sensor = this.Sensors[key];
        if (this.Devices.hasOwnProperty(sensor.device_id) == false) {
            continue;
        }

        if (this.Devices[sensor.device_id].status == false) {
            continue;
        }

        row = [];
        switch(sensor.type) {
            case 1:
                row.push(`<div><span data-feather="thermometer"></span></div>`);
                break;
            case 2:
                row.push(`<div><span data-feather="cloud-rain"></span></div>`);
                break;
            case 3:
                row.push(`<div><span data-feather="user"></span></div>`);
                break;
            case 4:
                row.push(`<div><span data-feather="sun"></span></div>`);
                break;
            default:
                row.push("");
        }
        row.push(`<h6 class="my-0"><a href="#" onclick="">`+sensor.name+`</a></h6>`);
        switch(sensor.type) {
            case 1:
                row.push(`<div>`+sensor.value+`</div>`);
                break;
            case 2:
                row.push(`<div>`+sensor.value+`</div>`);
                break;
            case 3:
                var color = "black";
                var icon = "user-minus";
                if (sensor.value == 1) {
                    color = "red";
                    icon = "user-plus";
                }
                var html = `<span style="color: `+color+`;cursor: pointer;" onclick="" data-feather="`+icon+`" id="id_m_sensor_`+sensor.id+`"></span>`;
                row.push(html);
                break;
            case 4:
                var html = "";
                if (sensor.value == 1) {
                    html = `
                        <div class="custom-control custom-switch">
                            <input type="checkbox" onclick="window.ApplicationModules.DashboardView.SwichOnclickEvent(`+sensor.device_id+`,`+sensor.index+`,'id_m_sensor_`+sensor.id+`');" checked class="custom-control-input" id="id_m_sensor_`+sensor.id+`">
                            <label class="custom-control-label" for="id_m_sensor_`+sensor.id+`"></label>
                        </div>
                    `;
                } else {
                    html = `
                        <div class="custom-control custom-switch">
                            <input type="checkbox" onclick="window.ApplicationModules.DashboardView.SwichOnclickEvent(`+sensor.device_id+`,`+sensor.index+`,'id_m_sensor_`+sensor.id+`');" class="custom-control-input" id="id_m_sensor_`+sensor.id+`">
                            <label class="custom-control-label" for="id_m_sensor_`+sensor.id+`"></label>
                        </div>
                    `;
                }
                row.push(html);
                break;
            default:
                row.push(`<div>`+sensor.value+`</div>`);
        }
        row.push(`<div>`+sensor.description+`</div>`);
        row.push(`<span style="color: green;cursor: pointer;" onclick="window.ApplicationModules.DashboardView.SensorSettingsOnclickEvent(`+sensor.device_id+`,`+sensor.index+`,'id_m_sensor_`+sensor.id+`');" data-feather="settings"></span>`);
        data.push(row);
    }
    table.ShowRowNumber(true);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_sensors_table"));
    feather.replace();
}

ModuleDashboardView.prototype.GetSensors = function() {
    var self = this;
}

ModuleDashboardView.prototype.GetDevicesEvent = function(data) {
    var self = this;

    var status_change = false;
    for (key in data) {
        var device = data[key];
        if (self.Devices.hasOwnProperty(device.device_id) == true) {
            if (this.Devices[device.device_id].status != device.status) {
                status_change = true;
            }
            this.Devices[device.device_id].status = device.status;
        }
    }

    if (status_change == true) {
        this.UpdateDevicesTable();
        this.UpdateSensorsTable();
    }
}

ModuleDashboardView.prototype.USBDeviceConnectedEvent = function(device) {
    var self = this;
    // { type": "GATEWAY | NODE", "port": [COMPORT], "index": DEVICE_ID }
    console.log("USBDeviceConnectedEvent", device);

    if (this.USBDevices.hasOwnProperty(device.port) == false) {
        this.USBDevices[device.port] = device;
    }

    // if Gateway type connected need to load system
    if (device.type == "GATEWAY") {
        this.LoadingProcess(function(obj) {

        });
    }

    this.UpdateUSBDevicesTable();
}

ModuleDashboardView.prototype.USBDeviceDisconnectedEvent = function(device) {
    var self = this;
    // { type": "GATEWAY | NODW", "port": [COMPORT], "index": DEVICE_ID }
    console.log("USBDeviceDisconnectedEvent", device);

    // if Gateway type disconnected need to unload system
    if (device.type == "GATEWAY") {
        this.GatewayOnline = false;
        this.Clean();
        this.LoadingProcess(function(obj) {

        });
    }

    delete this.USBDevices[device.port];
    this.UpdateUSBDevicesTable();
}

ModuleDashboardView.prototype.DeviceConnectionLostEvent = function(device_id) {
    var self = this;
    if (this.Devices.hasOwnProperty(device_id) == true) {
        var device = this.Devices[device_id];
        if (device.status == true) { 
            this.Devices[device_id].status = false;

            // Load sensor table
            this.LoadSensors(function(obj) {

            });
            // Update device table UI
            this.UpdateDevicesTable();
        }
    }
}

ModuleDashboardView.prototype.NRFDataEvent = function(data) {
    var self = this;
    console.log("NRFDataEvent", data.payload);
    if (this.Devices.hasOwnProperty(data.device_id) == true) {
        var device = this.Devices[data.device_id];
        device.sensors = data;
        if (device.status == false) {
            this.Devices[data.device_id].status = true;

            // Load sensor table
            this.LoadSensors(function(obj) {

            });
            // Update device table UI
            this.UpdateDevicesTable();
        }
    }

    for (key in data.sensors) {
        var item = data.sensors[key];
        if (this.Sensors.hasOwnProperty([data.device_id, item.index]) == true) {
            var sensor = this.Sensors[[data.device_id, item.index]];
            sensor.value = item.value;
        }
    }
    self.UpdateSensorsTable();
}

ModuleDashboardView.prototype.SwichOnclickEvent = function(device_id, index, id) {
    var obj = document.getElementById(id);

    var value = 0;
    if (obj.checked == true) {
        value = 1;
    }

    app.Adaptor.SetSensorDataRemote(device_id, index, value, function(data, error) {
        console.log("SetSensorDataRemote", data);
    });
}

ModuleDashboardView.prototype.SensorSettingsOnclickEvent = function(device_id, index, id) {
    var sensor = this.Sensors[[device_id, index]]
    this.ModuleSensorViewObj = new ModuleSensorView(this, sensor);
    this.ModuleSensorViewObj.SetObjectDOMName(this.DOMName+".ModuleSensorViewObj");
    this.ModuleSensorViewObj.Build(null, function(module) {
        window.ApplicationModules.Modal.Remove();
        window.ApplicationModules.Modal.SetTitle("Sensor");
        window.ApplicationModules.Modal.SetContent(module.HTML);
        window.ApplicationModules.Modal.SetFooter(`<button type="button" class="btn btn-success" onclick="window.ApplicationModules.DashboardView.ModuleSensorViewObj.Update();">Save</button><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.ApplicationModules.Modal.Build("lg");
        window.ApplicationModules.Modal.Show();
        module.Load();
    });
}

ModuleDashboardView.prototype.SettingsOnclickEvent = function(port) {
    var device = this.USBDevices[port];
    if (device.type == "NODE") {
        this.ModuleNodeViewObj = new ModuleNodeView(this, device);
        this.ModuleNodeViewObj.SetObjectDOMName(this.DOMName+".ModuleNodeViewObj");
        this.ModuleNodeViewObj.Build(null, function(module) {
            window.ApplicationModules.Modal.Remove();
            window.ApplicationModules.Modal.SetTitle("Node");
            window.ApplicationModules.Modal.SetContent(module.HTML);
            window.ApplicationModules.Modal.SetFooter(`<button type="button" class="btn btn-success" onclick="window.ApplicationModules.DashboardView.ModuleNodeViewObj.Update();">Save</button><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
            window.ApplicationModules.Modal.Build("lg");
            window.ApplicationModules.Modal.Show();
            module.Load();
        });
    } else {
        this.ModuleGatewayViewObj = new ModuleGatewayView(this, device);
        this.ModuleGatewayViewObj.SetObjectDOMName(this.DOMName+".ModuleGatewayViewObj");
        this.ModuleGatewayViewObj.Build(null, function(module) {
            window.ApplicationModules.Modal.Remove();
            window.ApplicationModules.Modal.SetTitle("Gateway");
            window.ApplicationModules.Modal.SetContent(module.HTML);
            window.ApplicationModules.Modal.SetFooter(`<button type="button" class="btn btn-success" onclick="window.ApplicationModules.DashboardView.ModuleGatewayViewObj.Update();">Save</button><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
            window.ApplicationModules.Modal.Build("lg");
            window.ApplicationModules.Modal.Show();
            module.Load();
        });
    }
}

ModuleDashboardView.prototype.DeleteDeviceOnclickEvent = function(device_id) {
    var self = this;
    var gateway = self.DefaultGateway;

    console.log(device_id);

    app.Adaptor.SetWorkingPort(gateway.port, function(data, error) {
        app.Adaptor.DeleteDevice(device_id, function(data, error) {
            app.Adaptor.DelNodeIndexHandler(device_id, function(data, error) {
                console.log("Node deleted from gateway", data.payload.device_id);
                self.Clean();
                self.LoadingProcess();
            });
        });
    });
}

ModuleDashboardView.prototype.AppendDeviceOnclickEvent = function(device_type, device_id) {
    var self = this;
    var gateway = self.DefaultGateway;

    if (self.Devices.hasOwnProperty(device_id) == false) {
        app.Adaptor.SetWorkingPort(gateway.port, function(data, error) {
            app.Adaptor.InsertDevice(device_type, device_id, function(data, error) {
                app.Adaptor.AddNodeIndexHandler(device_id, function(data, error) {
                    self.Clean();
                    self.LoadingProcess();
                });
            });
        });
    } else {
        console.log("Cannot add existed device.", device_id);
    }
}
