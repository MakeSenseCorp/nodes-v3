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
    // Portfolio
    this.PortfolioID 	            = 0;
    this.PortfolioName              = "All";

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

ModuleStockAppend.prototype.AppendStock = function() {
    var self = this;
    var ticker = document.getElementById('d_m_stock_append_stock_find_ticker').value;
    node.API.SendCustomCommand(NodeUUID, "db_insert_stock", {
        'ticker': ticker
    }, function(res) {
        var payload = res.data.payload;
        self.GetDataBaseStocks();
    });
}

ModuleStockAppend.prototype.DeleteStock = function(ticker) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "db_delete_stock", {
        'ticker': ticker
    }, function(res) {
        var payload = res.data.payload;
        self.GetDataBaseStocks();
    });
}

ModuleStockAppend.prototype.FindStockInMarket = function() {
    var ticker = document.getElementById('d_m_stock_append_stock_find_ticker').value;
    document.getElementById('id_m_stock_append_info_container').innerHTML = "";

    this.StockGraph = new ModuleStockHistoryGraph("stock_market", ticker);
    this.StockGraph.SetHostingID("d_m_stock_append_stock_graph");
    this.StockGraph.SetObjectDOMName(this.DOMName+".StockGraph");
    this.StockGraph.Build(null, null);

    document.getElementById('id_m_stock_append_add_new_stock').classList.add("d-none");
    // document.getElementById('id_m_stock_append_stock_stocks_view').classList.add("d-none");
    var info = new ModuleStockInfo();
    info.SetHostingID("id_m_stock_append_info_container");
    info.Build(null, function(module) {
        module.GetStockInfo(ticker, function(module) {
            document.getElementById('id_m_stock_append_add_new_stock').classList.remove("d-none");
            // document.getElementById('id_m_stock_append_stock_stocks_view').classList.remove("d-none");
        });
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

ModuleStockAppend.prototype.UpdateStockTableFromLocalMarket = function() {
    for (key in market.Stocks) {
        var stock = market.Stocks[key];
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker).innerHTML = stock.market_price;
    }
}

ModuleStockAppend.prototype.UpdateStockTableAsync = function(data, scope) {
    for (key in data) {
        var stock = data[key];
        if (document.getElementById("id_m_stock_append_table_price_"+stock.ticker) === undefined || document.getElementById("id_m_stock_append_table_price_"+stock.ticker) === null) {
            return;
        }
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker).innerHTML = stock.market_price;
    }
}

ModuleStockAppend.prototype.GetDataBaseStocks = function() {
    var self = this;
    
    node.API.SendCustomCommand(NodeUUID, "get_db_stocks", {
    }, function(res) {
        var payload = res.data.payload;
        var table = new MksBasicTable();
        table.SetSchema(["", "", "", "", "", "", ""]);
        var data = [];
        for (key in payload.stocks) {
            stock = payload.stocks[key];
            row = [];
            row.push(`<h6 class="my-0"><a href="#" onclick="`+self.DOMName+`.UpdateStockInfoView('`+stock.ticker+`');">`+stock.ticker+`</a></h6>`);
            row.push(0);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`">`+stock.market_price+`<span>`);
            row.push(0);
            row.push(`
                <strong><span class="align-middle" style="color: RED; cursor: pointer;" onclick="">Buy</span></strong>
            `);
            row.push(`
                <strong><span class="align-middle" style="color: GREEN; cursor: pointer;" onclick="">Sell</span></strong>
            `);
            row.push(`
                <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle btn-sm" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        <span data-feather="menu"></span>
                    </button>
                    <div class="dropdown-menu text-center" aria-labelledby="dropdownMenuButton">
                        <span class="dropdown-item" style="color: BLUE; cursor:pointer" onclick="`+self.DOMName+`.OpenPortfolioSelectorModal('`+stock.ticker+`');">Portfolios</span>
                        <span class="dropdown-item" style="color: RED; cursor:pointer" onclick="`+self.DOMName+`.DeleteStock(`+stock.ticker+`');">Delete</span>
                    </div>
                </div>
            `);

            data.push(row);
        }
        table.ShowRowNumber(false);
        table.ShowHeader(false);
        table.SetData(data);
        table.Build(document.getElementById("id_m_stock_append_stock_table"));

        document.getElementById('d_m_stock_append_stock_find_ticker').addEventListener('keyup', function(event) {
            if (event.code === 'Enter') {
                event.preventDefault();
                self.FindStockInMarket(document.getElementById('d_m_stock_append_stock_find_ticker').value);
            }
        });
        // document.getElementById('id_m_stock_append_stock_stocks_view').classList.remove("d-none");
        feather.replace();
        self.UpdateStockTableFromLocalMarket();
    });
}

ModuleStockAppend.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockAppend.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}