function ModuleStockDetails() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;
    this.HistoryDataGraphObject 	= null;
    this.HistogrameDataGraphObject 	= null;
    this.StockDetailsDataObject 	= null;
    this.StockActionsHistoryObject 	= null;

    return this;
}

ModuleStockDetails.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockDetails.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStockDetails.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleStockDetails.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        
        // document.getElementById(self.HostingID).innerHTML = self.HTML;
        // self.HistoryDataGraphObject     = document.getElementById("id_history_stock_data");
        // self.HistogrameDataGraphObject  = document.getElementById("id_histograme_stock_data");

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleStockDetails.prototype.GetDetails = function(ticker) {
    if (ticker === undefined || ticker === null) {
        return false;
    }

    this.StockDetailsDataObject     = document.getElementById("id_m_stock_details_info_container");
    this.StockActionsHistoryObject  = document.getElementById("id_stock_history_list");
    this.ComponentObject            = document.getElementById("id_m_stock_details_"+this.HostingID);
    this.Hide();

    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_stock_history", {
        "ticker": ticker
    }, function(res) {
        var payload = res.data.payload;
        var table = new MksBasicTable();
        table.SetSchema(["","Date","Price", "Amount", "Action"]);
        var data = [];
        for (key in payload.history) {
            stock = payload.history[key];
            row = [];
            row.push(stock.date);
            row.push(stock.price);
            row.push(stock.amount);
            if (stock.action < 0) {
                row.push("<span style='color:RED'>BUY</span>");
            } else {
                row.push("<span style='color:GREEN'>SELL</span>");
            }
            data.push(row);
        }
        table.SetData(data);
        table.Build(self.StockActionsHistoryObject);
    });

    // ui.HistogrameGraph 	= new MksBasicGraph("histograme");
    // ui.BuilsHistogrameGraph(payload);

    var info = new ModuleStockInfo();
    info.SetHostingID("id_m_stock_details_info_container");
    info.Build(null, function(module) {
        module.GetStockInfo(ticker);
    });

    this.GraphModule = new ModuleStockHistoryGraph("stock_graph", ticker);
    this.GraphModule.SetHostingID("id_m_stock_history_graph_container");
    this.GraphModule.SetObjectDOMName(this.DOMName+".GraphModule");
    this.GraphModule.Build(null, null);

    this.Show();
}

ModuleStockDetails.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockDetails.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}