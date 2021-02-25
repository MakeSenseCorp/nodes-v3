function ModuleStockAppend() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;
    this.StockGraph                 = null;
    this.Selector                   = null;

    return this;
}

ModuleStockAppend.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockAppend.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStockAppend.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleStockAppend.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);

        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            self.HostingObject.innerHTML = self.HTML;
        }
       
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleStockAppend.prototype.ShowStockAppendCheckbox = function(obj) {
    if (obj.checked == true) {
        document.getElementById("id_m_stock_append_stock_table").classList.remove("d-none");
    } else {
        document.getElementById("id_m_stock_append_stock_table").classList.add("d-none");
    }
}

ModuleStockAppend.prototype.FindStockInMarket = function() {
    var ticker = document.getElementById('d_m_stock_append_stock_find_ticker').value;

    this.StockGraph = new ModuleStockHistoryGraph("stock_market", ticker);
    this.StockGraph.SetHostingID("d_m_stock_append_stock_graph");
    this.StockGraph.SetObjectDOMName(this.DOMName+".StockGraph");
    this.StockGraph.Build(null, null);

    var info = new ModuleStockInfo();
    info.SetHostingID("id_m_stock_append_info_container");
    info.Build(null, function(module) {
        module.GetStockInfo(ticker);
    });
}

ModuleStockAppend.prototype.OpenPortfolioSelectorModal = function(ticker) {
    this.Selector = new ModulePortfolioSelectorView(ticker);
    this.Selector.SetObjectDOMName(this.DOMName+".Selector");
    this.Selector.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Portfolios");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("sm");
        window.Modal.Show();
    });
}

ModuleStockAppend.prototype.UpdateStockInfoView = function(ticker) {
    document.getElementById('d_m_stock_append_stock_find_ticker').value = ticker;
    this.FindStockInMarket();
}

ModuleStockAppend.prototype.GetDataBaseStocks = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_db_stocks", {
    }, function(res) {
        var payload = res.data.payload;
        var stockTable = new MksBlockTable();
        var tableData = []
        
        for (key in payload.stocks) {
            stock = payload.stocks[key];
            var ticker = `<a href="#" onclick="[DOM].UpdateStockInfoView('[TICKER]');">[TICKER]</a>`;
            var options = `
                            <div class="row">
                                <div class="col">
                                    <div class="dropdown">
                                        <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            Options
                                        </button>
                                        <div class="dropdown-menu text-center" aria-labelledby="dropdownMenuButton">
                                            <span class="dropdown-item" style="color: BLUE; cursor:pointer" onclick="[DOM].OpenPortfolioSelectorModal('[TICKER]');">Portfolios</span>
                                            <span class="dropdown-item" style="color: RED; cursor:pointer">Delete</span>
                                        </div>
                                    </div>
                                </div>
                            </div>`;
            ticker = ticker.split("[DOM]").join(self.DOMName);
            ticker = ticker.split("[TICKER]").join(stock.ticker);
            options = options.split("[DOM]").join(self.DOMName);
            options = options.split("[TICKER]").join(stock.ticker);
            tableData.push({
                "item1": ticker,
                "item2": stock.name,
                "item3": options
            });
        }
        stockTable.SetData(tableData);
        stockTable.Build(document.getElementById("id_m_stock_append_stock_table"));

        document.getElementById('d_m_stock_append_stock_find_ticker').addEventListener('keyup', function(event) {
            if (event.code === 'Enter') {
                event.preventDefault();
                self.FindStockInMarket(document.getElementById('d_m_stock_append_stock_find_ticker').value);
            }
        });
    });
}

ModuleStockAppend.prototype.AppendStock = function(ticker) {

}

ModuleStockAppend.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockAppend.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}