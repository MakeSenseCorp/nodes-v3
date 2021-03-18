function ModuleDashboardView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;

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

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleDashboardView.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        self.ComponentObject = document.getElementById("id_m_stocks_view_"+this.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleDashboardView.prototype.Clean = function() {
    clearInterval(this.GetStocksTimerHndl);
}

ModuleDashboardView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleDashboardView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}