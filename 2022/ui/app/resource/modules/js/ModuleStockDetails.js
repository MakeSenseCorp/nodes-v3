function ModuleStockDetails() {
    var self = this;

    // Modules basic
    this.HTML 	                    = `
        <div class="row" id="id_m_stock_details_[ID]" class="d-none">
            <div class="col-lg-12">
                <div class="row">
                    <div class="col-lg-12">
                        <h5 class="mb-3">History</h5>
                    </div>
                </div>
            </div>
            <div class="col-lg-12">
                <div class="row">
                    <div class="col-lg-12">
                        <div id="id_stock_history_list"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
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
    self.HTML = self.HTML.replace("[ID]", this.HostingID);
    if (callback !== undefined && callback != null) {
        callback(this);
    }
}

ModuleStockDetails.prototype.DeleteAction = function(ticker, id) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "db_delete_action", {
        "ticker": ticker,
        "id": id
    }, function(res) {
        var payload = res.data.payload;
        self.GetDetails(ticker);
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
        console.log(payload);
        var table = new MksBasicTable();
        table.SetSchema(["","", "", "",""]);
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
            row.push(`<span style="color:RED; cursor: pointer" onclick="`+self.DOMName+`.DeleteAction('`+ticker+`',`+stock.id+`)">Delete</span>`);
            data.push(row);
        }
        table.ShowRowNumber(false);
        table.ShowHeader(false);
        table.SetData(data);
        table.Build(self.StockActionsHistoryObject);
    });

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