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

    this.USBDevices                 = {};
    this.Devices                    = {};
    this.Sensors                    = {};
    this.System                     = null;

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

        app.Adaptor.GetSystemInfo(function(data, error) {
            var system = data.payload.system;
            self.System = system;
            var gateways = system.local_db.gateways;
            var nodes = system.local_db.nodes;
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
            self.UpdateUSBDevicesTable();

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
    
                var gateway = self.System.local_db.gateways[Object.keys(self.System.local_db.gateways)[0]];
                app.Adaptor.SetWorkingPort(gateway.port, function(data, error) {
                    app.Adaptor.ListNodes(function(data, error) {
                        var nodes = data.payload.list;
                        for (key in nodes) {
                            var node = nodes[key];
                            self.Devices[node.device_id].status = node.status;
                        }
                        self.UpdateDevicesTable();
                    })
                });
            });

            app.Adaptor.SelectSensors(function(data, error) {
                var sensors = data.payload;
                for (key in sensors) {
                    var sensor = sensors[key];
                    sensor.value = 0;
                    self.Sensors[[sensor.device_id, sensor.index]] = sensor;
                }
                self.UpdateSensorsTable();
            })
        });
    });
}

ModuleDashboardView.prototype.Clean = function() {
}

ModuleDashboardView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleDashboardView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}

ModuleDashboardView.prototype.UpdateUSBDevicesTable = function() {
    var self = this;

    var data = [];
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", ""]);
    for (key in this.USBDevices) {
        var device = this.USBDevices[key];
        row = [];
        row.push(`<h6 class="my-0"><a href="#" onclick="">`+device.type+`</a></h6>`);
        row.push(`<div>`+device.port+`</div>`);
        row.push(`<div>`+device.index+`</div>`);
        row.push(`<div><span style="color: green; cursor: pointer;">Connected</span></div>`);
        data.push(row);
    }
    table.ShowRowNumber(true);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_usb_device_table"));
}

ModuleDashboardView.prototype.UpdateDevicesTable = function() {
    var self = this;

    var data = [];
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", "", ""]);
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
        row.push(`<span style="color: red;cursor: pointer;" onclick="" data-feather="delete"></span>`);
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
    table.SetSchema(["", "", "", ""]);
    for (key in this.Sensors) {
        var sensor = this.Sensors[key];
        row = [];
        row.push(`<h6 class="my-0"><a href="#" onclick="">`+sensor.name+`</a></h6>`);
        switch(sensor.type) {
            case 1:
                row.push(`<div>`+sensor.value+` C</div>`);
                break;
            case 2:
                row.push(`<div>`+sensor.value+` H</div>`);
                break;
            case 3:
                row.push(`<div>`+sensor.value+`</div>`);
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
        row.push(`<div>`+sensor.type+`</div>`);
        row.push(`<div>`+sensor.description+`</div>`);
        row.push(`<div><span style="color: green; cursor: pointer;">`+sensor.enabled+`</span></div>`);
        data.push(row);
    }
    table.ShowRowNumber(true);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_sensors_table"));
}

ModuleDashboardView.prototype.GetSensors = function() {
    var self = this;
}

ModuleDashboardView.prototype.GetDevices = function() {
    var self = this;
}

ModuleDashboardView.prototype.DeviceConnectedEvent = function(device) {
    var self = this;
    // { type": "GATEWAY | NODW", "port": [COMPORT], "index": DEVICE_ID }
    if (this.USBDevices.hasOwnProperty(device.port) == false) {
        this.USBDevices[device.port] = device;
    }

    this.UpdateUSBDevicesTable();
}

ModuleDashboardView.prototype.DeviceDisconnectedEvent = function(device) {
    var self = this;
    // { type": "GATEWAY | NODW", "port": [COMPORT], "index": DEVICE_ID }
    delete this.USBDevices[device.port];

    this.UpdateUSBDevicesTable();
}

ModuleDashboardView.prototype.DeviceConnectionLostEvent = function(device_id) {
    var self = this;
    if (this.Devices.hasOwnProperty(device_id) == true) {
        var device = this.Devices[device_id];
        if (device.status == true) { 
            this.Devices[device_id].status = false;
            this.UpdateDevicesTable();
        }
    }
}

ModuleDashboardView.prototype.NRFDataEvent = function(data) {
    var self = this;
    if (this.Devices.hasOwnProperty(data.device_id) == true) {
        var device = this.Devices[data.device_id];
        device.sensors = data;
        if (device.status == false) {
            this.Devices[data.device_id].status = true;
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
        console.log(data);
    });
}
