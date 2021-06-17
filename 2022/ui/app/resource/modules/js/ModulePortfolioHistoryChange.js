function ModulePortfolioHistoryChange(ticker) {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;

    return this;
}

ModulePortfolioHistoryChange.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModulePortfolioHistoryChange.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModulePortfolioHistoryChange.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModulePortfolioHistoryChange.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("ModulePortfolioHistoryChange", "id_m_portfolio_history_change_"+self.HostingID);
        
        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            self.HostingObject.innerHTML = self.HTML;
        }

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModulePortfolioHistoryChange.prototype.Start = function(portfolio_id) {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "portfolio_history_change", {
        "portfolio_id": portfolio_id
    }, function(res) {
        var payload = res.data.payload;
    });
}

ModulePortfolioHistoryChange.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModulePortfolioHistoryChange.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}