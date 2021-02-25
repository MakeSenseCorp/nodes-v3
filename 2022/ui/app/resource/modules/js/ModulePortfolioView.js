function ModulePortfolioView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    this.PortfolioList              = [];
    // Objects section
    this.ComponentObject            = null;
    this.HistoryDataGraphObject 	= null;

    return this;
}

ModulePortfolioView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModulePortfolioView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModulePortfolioView.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModulePortfolioView.html"
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

ModulePortfolioView.prototype.UpdatePortfolioList = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        var obj = document.getElementById("id_m_portfolio_name_list");

        self.PortfolioList = payload.portfolios;
        var table = new MksBasicTable();
        table.SetSchema(["","Portfolio Name", "Edit", "Stocks", "Delete"]);
        var data = [];
        for (key in payload.portfolios) {
            portfolio = payload.portfolios[key];
            row = [];
            row.push(portfolio.name);
            row.push("<a href='#' onclick='window.Portfolio.EditPortfolio("+portfolio.id+")'><span>Edit</span></a>");
            row.push("<a href='#' onclick='window.Portfolio.OpenStockViewer("+portfolio.id+")'><span>View Stocks</span></a>");
            row.push("<a href='#' onclick='window.Portfolio.DeletePortfolio("+portfolio.id+")'><span>Delete</span></a>");
            data.push(row);
        }
        table.SetData(data);
        table.Build(obj);
    });
}

ModulePortfolioView.prototype.CreatePortfolio = function() {
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
        self.UpdatePortfolioList();
    });
}

ModulePortfolioView.prototype.DeletePortfolio = function(id) {
    var self = this;
}

ModulePortfolioView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModulePortfolioView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}