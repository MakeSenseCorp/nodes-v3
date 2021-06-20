function ModulePortfolioHistoryChange(ticker) {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;
    this.PortfolioId                = -1;

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

ModulePortfolioHistoryChange.prototype.SetPotfolioId = function(portfolio_id) {
    this.PortfolioId = portfolio_id;
}

ModulePortfolioHistoryChange.prototype.GetStockList = function() {
    console.log("GetStockList", this.PortfolioId);
    
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": this.PortfolioId
    }, function(res) {
        var payload = res.data.payload;
        console.log(payload);
    });
}

ModulePortfolioHistoryChange.prototype.Start = function() {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "portfolio_history_change", {
        "portfolio_id": this.PortfolioId
    }, function(res) {
        var payload = res.data.payload;
        console.log(payload);
        if (payload.status == true) {

        } else {

        }
    });
}

ModulePortfolioHistoryChange.prototype.TableUIChangeEvent = function() {
    feather.replace();
}

ModulePortfolioHistoryChange.prototype.UpdateStatistics = function(output) {
    var data  = [];
    var table = new MksBasicTable();

    table.EnableListing();
    table.SetListingWindowSize(15);
    table.RegisterUIChangeEvent(this.TableUIChangeEvent);
    table.SetSchema(["Ticker", "Sum", "Total Diff", "Data"]);

    for (key in output.stocks) {
        var stock = output.stocks[key];
        var row = [];
        var color = "black";

        row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer" >`+stock.ticker+`</a></h6>`);
        if (stock.sum_diff < 0) {
            color = "red";
        } else {
            color = "green";
        }
        row.push(`<span style="color:`+color+`">`+stock.sum_diff.toFixed(2)+`</span>`);
        if (stock.total_diff < 0) {
            color = "red";
        } else {
            color = "green";
        }
        row.push(`<span style="color:`+color+`">`+stock.total_diff.toFixed(2)+`</span>`);
        row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer" onclick="">Data</a></h6>`);
        data.push(row);
    }

    console.log(data);

    table.ShowRowNumber(false);
    table.ShowHeader(true);
    table.SetData(data);
    table.Build(document.getElementById("id_m_portfolio_history_change_output_table"));
    feather.replace();
}

ModulePortfolioHistoryChange.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModulePortfolioHistoryChange.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}