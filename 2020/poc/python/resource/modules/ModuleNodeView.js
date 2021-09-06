function ModuleNodeView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;

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
