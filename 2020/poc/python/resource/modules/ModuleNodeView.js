function ModuleNodeView(obj, device) {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;

    this.DasboardModule             = obj;
    this.Device                     = device;

    return this;
}

ModuleNodeView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleNodeView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleNodeView.prototype.Build = function(data, callback) {
    var self = this;

    app.API.GetFileContent({
        "file_path": "modules/ModuleNodeView.html"
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
    });
}

ModuleNodeView.prototype.Clean = function() {
}

ModuleNodeView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleNodeView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}

ModuleNodeView.prototype.Load = function() {
    var self = this;

    this.UpdateSensorsTable();

    document.getElementById("id_m_port").innerHTML = this.Device.port;
    document.getElementById("id_m_device_index_dropdown_span").innerHTML = this.Device.index;
}

ModuleNodeView.prototype.UpdateSensorsTable = function() {
    var self = this;

    var data = [];
    var table = new MksBasicTable();
    table.SetSchema(["", "", ""]);
    for (key in this.DasboardModule.Sensors) {
        var sensor = this.DasboardModule.Sensors[key];
        if (this.DasboardModule.Devices[sensor.device_id].status == false) {
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
        row.push(`<div>`+sensor.description+`</div>`);
        data.push(row);
    }
    table.ShowRowNumber(true);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_remote_sensors_table"));
    feather.replace();
}

ModuleNodeView.prototype.SelectIndex = function(index) {
    document.getElementById("id_m_device_index_dropdown_span").innerHTML = index;
}

ModuleNodeView.prototype.Update = function() {
    var self = this;
    // Set working port to this deivce.
    app.Adaptor.SetWorkingPort(this.Device.port, function(data, error) {
        // Send index device update.
        var index = parseInt(document.getElementById("id_m_device_index_dropdown_span").innerHTML);
        app.Adaptor.SetNodeAddress(index, function(data, error) {
            // Update dasboard
            self.DasboardModule.USBDevices[self.Device.port].index = index;
            // Set working port to Gateway.
            app.Adaptor.SetWorkingPort(self.DasboardModule.DefaultGateway.port, function(data, error) {
                self.DasboardModule.LoadingProcess();
                window.ApplicationModules.Modal.Hide();
            });
        });
    });
}
