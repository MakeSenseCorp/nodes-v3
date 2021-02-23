function ModulePortfolio() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    this.PortfolioListID            = "";
    this.PortfolioList              = [];
    // Objects section
    this.ComponentObject            = null;
    this.HistoryDataGraphObject 	= null;

    return this;
}

ModulePortfolio.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModulePortfolio.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModulePortfolio.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModulePortfolio.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);

        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            this.ComponentObject = document.getElementById("id_m_portfolio_"+this.HostingID);
            self.HostingObject.innerHTML = self.HTML;
        }
        
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModulePortfolio.prototype.UpdatePortfolioList = function(hosting_id) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        this.PortfolioListID = hosting_id;
        var obj = document.getElementById(this.PortfolioListID);

        self.PortfolioList = payload.portfolios;
        obj.innerHTML = "<option value='0'>All</option>";
        for (key in payload.portfolios) {
            item = payload.portfolios[key];
            obj.innerHTML += "<option value='" + item.id + "'>" + item.name + "</option>";
        }
    });
}

ModulePortfolio.prototype.CreatePortfolio = function() {
    var self = this;
    var portfolioName = document.getElementById("id_m_portfolio_name").value;
    if (portfolioName === undefined || portfolioName === null || portfolioName == "") {
        alert("Something wrong with Portfolio name");
        return;
    }
    node.API.SendCustomCommand(NodeUUID, "create_new_portfolio", {
        "name": document.getElementById("id_m_portfolio_name").value 
    }, function(res) {
        var payload = res.data.payload;
        self.UpdatePortfolioList(self.PortfolioListID);
        window.Modal.Hide();
        window.Modal.Remove();
    });
}

ModulePortfolio.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModulePortfolio.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}