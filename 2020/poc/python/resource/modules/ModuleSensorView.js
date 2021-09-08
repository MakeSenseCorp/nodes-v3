function ModuleSensorView(obj, sensor) {
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
    this.Sensor                     = sensor;

    return this;
}

ModuleSensorView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleSensorView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleSensorView.prototype.Build = function(data, callback) {
    var self = this;

    app.API.GetFileContent({
        "file_path": "modules/ModuleSensorView.html"
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

        // html = html.split("[ID]").join(sensor.id);
    });
}

ModuleSensorView.prototype.Clean = function() {
}

ModuleSensorView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleSensorView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}

ModuleSensorView.prototype.Load = function() {
    var self = this;

    document.getElementById("id_m_name").value = this.Sensor.name;
    document.getElementById("id_m_description").value = this.Sensor.description;
}

ModuleSensorView.prototype.Update = function() {
    var self = this;
    app.Adaptor.SetWorkingPort(this.DasboardModule.DefaultGateway.port, function(data, error) {
        var name = document.getElementById("id_m_name").value;
        var decription = document.getElementById("id_m_description").value;
        app.Adaptor.UpdateSensorInfo(self.Sensor.id, name, decription, function(data, error) {
            self.DasboardModule.LoadSensors();
            window.ApplicationModules.Modal.Hide();
        });
    });
}
