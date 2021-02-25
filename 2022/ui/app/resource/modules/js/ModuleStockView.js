function ModuleStockView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    this.PortfolioList              = [];
    this.GetStocksTimerHndl         = 0;
    this.StockLoaderProgressBar	    = null;
    this.PortfolioID 	            = 0;
    this.PortfolioName              = "";
    // Objects section
    this.ComponentObject            = null;

    return this;
}

ModuleStockView.prototype.PortfolioOnChangeHandler = function(obj) {
    var self = this;

    this.PortfolioID   = obj.value;
    this.PortfolioName = obj.options[obj.value].text;
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": parseInt(obj.value),
        "portfolio_name": this.PortfolioName
    }, function(res) {
        var payload = res.data.payload;
        self.RebuildPortfolioEarnings(payload.portfolio);
        self.RebuildStockTable(payload.stocks);
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
        self.ComponentObject = document.getElementById("id_m_stocks_view_"+this.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;

        self.objStockTable              = document.getElementById("id_stocks_list");
        self.objPortfolioEarnings       = document.getElementById("id_portfolio_earnings");
        self.objPortfolioStocksNumber   = document.getElementById("id_portfolio_number_of_stocks");
        self.objPortfolioInvestment     = document.getElementById("id_portfolio_investment");
        self.objPortfolioStocksCount    = document.getElementById("id_portfolio_stocks_count");

        self.StockLoaderProgressBar	= new MksBasicProgressBar("StockLoaderProgressBar");
        self.StockLoaderProgressBar.EnableInnerPercentageText(false);
        self.StockLoaderProgressBar.Build(document.getElementById("id_stocks_loading_progressbar"));
        self.StockLoaderProgressBar.Show();

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
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": parseInt(this.PortfolioID),
        "portfolio_name": this.PortfolioName
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
        
        self.objPortfolioEarnings.innerHTML = portfolio.earnings;
        if (portfolio.earnings < 0) {
            self.objPortfolioEarnings.style.color = "RED";
        } else {
            self.objPortfolioEarnings.style.color = "GREEN";
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
            self.StockLoaderProgressBar.UpdateProgress({
                'precentage': payload.status.percentage,
                'message': "Loading (" + payload.status.percentage + "%)"
            });
            setTimeout(self.GetStocks.bind(self), 2500);
            return;
        }

        self.StockLoaderProgressBar.Hide();
        self.RebuildPortfolioEarnings(payload.portfolio);
        self.RebuildStockTable(payload.stocks);
        self.GetStocksTimerHndl = setInterval(self.UpdateStocksPrice.bind(self), 10000);
    });
}

ModuleStockView.prototype.UpdatePortfolioList = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        var obj = document.getElementById("id_selected_portfolio");

        self.PortfolioList = payload.portfolios;
        obj.innerHTML = "<option value='0'>All</option>";
        for (key in payload.portfolios) {
            item = payload.portfolios[key];
            obj.innerHTML += "<option value='" + item.id + "'>" + item.name + "</option>";
        }
    });
}

ModuleStockView.prototype.Clean = function() {
    clearInterval(this.GetStocksTimerHndl);
}

ModuleStockView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}