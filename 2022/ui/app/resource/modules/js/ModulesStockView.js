function ModuleStockView() {
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

var g_portfolio_id 	 = 0;
var g_portfolio_name = "";

ModuleStockView.prototype.PortfolioOnChangeHandler = function(obj) {
    g_portfolio_id   = obj.value;
    g_portfolio_name = obj.options[obj.value].text;
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": parseInt(obj.value),
        "portfolio_name": g_portfolio_name
    }, function(res) {
        var payload = res.data.payload;
        ui.RebuildPortfolioEarnings(payload.portfolio);
        ui.RebuildStockTable(payload.stocks);
    });
};

ModuleStockView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStockView.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleStockView.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        // this.ComponentObject = document.getElementById("id_m_portfolio_"+this.HostingID);
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleStockView.prototype.RebuildPortfolioEarnings = function(portfolio) {
    this.objPortfolioInvestment.innerHTML = portfolio.investment;
    this.objPortfolioStocksCount.innerHTML = portfolio.stocks_count;
    this.objPortfolioEarnings.innerHTML = portfolio.earnings;
    if (portfolio.earnings < 0) {
        this.objPortfolioEarnings.style.color = "RED";
    } else {
        this.objPortfolioEarnings.style.color = "GREEN";
    }
}

ModuleStockView.prototype.UpdateStocksPrice = function() {
    self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": parseInt(g_portfolio_id),
        "portfolio_name": g_portfolio_name
    }, function(res) {
        var payload = res.data.payload;
        var portfolio = payload.portfolio;

        for (key in payload.stocks) {
            var stock = payload.stocks[key];
            var obj = document.getElementById("id_stock_table_price_" + stock.ticker);
            obj.innerHTML = stock.market_price;
            obj = document.getElementById("id_stock_table_earnings_" + stock.ticker);
            obj.innerHTML = "(" + stock.earnings + ")";
        }
        
        ui.objPortfolioEarnings.innerHTML = portfolio.earnings;
        if (portfolio.earnings < 0) {
            ui.objPortfolioEarnings.style.color = "RED";
        } else {
            ui.objPortfolioEarnings.style.color = "GREEN";
        }
    });
}

ModuleStockView.prototype.RebuildStockTable = function(stocks) {
    var tableContent = "";
    var portfolioStocksCount = 0.0;

    var ui_size = "lg";
    if (stocks.length > 30) {
        ui_size = "sm";
    }

    var row = new ModuleRowStock();
    for (key in stocks) {
        var stock 	  = stocks[key];
        stock.ui_size = ui_size;
        tableContent += row.Build(stock);
        portfolioStocksCount += stock.number;
    }
    
    this.objStockTable.innerHTML = tableContent;
    this.objPortfolioStocksNumber.innerHTML = portfolioStocksCount;
    $('[data-toggle="tooltip"]').tooltip();
}

ModuleStockView.prototype.GetStocks = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": 0,
        "portfolio_name": "All"
    }, function(res) {
        var payload = res.data.payload;
        if (payload.status.local_stock_market_ready == false) {
            ui.StockLoaderProgressBar.UpdateProgress({
                'precentage': payload.status.percentage,
                'message': "Loading (" + payload.status.percentage + "%)"
            });
            setTimeout(ui.GetStocks, 2500);
            return;
        }

        ui.StockLoaderProgressBar.Hide();
        ui.RebuildPortfolioEarnings(payload.portfolio);
        ui.RebuildStockTable(payload.stocks);
        node.GetStocksTimerHndl = setInterval(ui.UpdateStocksPrice, 10000);
    });
}

ModuleStockView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}