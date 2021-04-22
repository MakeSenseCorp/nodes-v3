function ModuleSettingsView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;
    this.DBStatus                   = "IDLE";

    return this;
}

ModuleSettingsView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleSettingsView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleSettingsView.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleSettingsView.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        self.ComponentObject = document.getElementById("id_m_funder_settings_view_"+this.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;

        if (callback !== undefined && callback != null) {
            callback(self);
        }

        setTimeout(self.FunderStatus.bind(self), 2.5);
    });
}

ModuleSettingsView.prototype.Clean = function() {
    clearInterval(this.GetStocksTimerHndl);
}

ModuleSettingsView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleSettingsView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}

ModuleSettingsView.prototype.FunderStatus = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "confuguration", {
        "operation": "status"
    }, function(res) {
        var payload = res.data.payload;
        document.getElementById("id_m_funder_settings_view_db_status").innerHTML = payload.update_status.status;
        if (payload.update_status.working == true) {
            document.getElementById("id_m_funder_settings_view_update_db_button").innerHTML = "Stop";
            document.getElementById("id_m_funder_settings_view_update_db_update_perc").innerHTML = payload.update_status.update_perc.toFixed(2) + "%";
        } else {
            document.getElementById("id_m_funder_settings_view_update_db_button").innerHTML = "Start";
            document.getElementById("id_m_funder_settings_view_update_db_update_perc").innerHTML = "";
        }
        setTimeout(self.FunderStatus.bind(self), 5000);
    });
}

ModuleSettingsView.prototype.UpdateDB = function(obj) {
    if (obj.innerHTML == "Start") {
        node.API.SendCustomCommand(NodeUUID, "confuguration", {
            "operation": "update_start"
        }, function(res) {
            var payload = res.data.payload;
            if (payload.status == true) {
                obj.innerHTML = "Stop";
            }
        });
    } else {
        node.API.SendCustomCommand(NodeUUID, "confuguration", {
            "operation": "update_stop"
        }, function(res) {
            var payload = res.data.payload;
            if (payload.status == true) {
                obj.innerHTML = "Start";
            }
        });
    }
    
}
