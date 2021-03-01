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
    this.PortfolioStocksCount       = 0;
    // Objects section
    this.ComponentObject            = null;

    return this;
}

ModuleStockView.prototype.PortfolioOnChangeHandler = function(obj) {
    var self = this;

    this.PortfolioID                = obj.value;
    this.PortfolioName              = obj.options[obj.selectedIndex].text;
    this.objStockTable.innerHTML    = "";
    this.PortfolioStocksCount       = 0;
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": parseInt(obj.value),
        "portfolio_name": this.PortfolioName
    }, function(res) {
        var payload = res.data.payload;
        self.RebuildPortfolioEarnings(payload.portfolio);
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
    this.objPortfolioInvestment.innerHTML   = portfolio.investment;
    this.objPortfolioStocksCount.innerHTML  = portfolio.stocks_count;
    this.objPortfolioEarnings.innerHTML     = portfolio.earnings;
    if (portfolio.earnings < 0) {
        this.objPortfolioEarnings.style.color = "RED";
    } else {
        this.objPortfolioEarnings.style.color = "GREEN";
    }
}

ModuleStockView.prototype.BuildStockAsync = function(stock) {
    var row = new ModuleRowStock();
    document.getElementById("id_m_stock_view_loader_ui").classList.add("d-none");
    stock.ui_size = "sm";
    if (row.RowExist(stock.ticker) == false) {
        this.objStockTable.innerHTML += row.Build(stock);
        this.PortfolioStocksCount += stock.number;
    }

    row.SetTicker(stock.ticker);
    row.SetPrice(stock.ticker, stock.market_price);
    row.SetAmomunt(stock.ticker, stock.number);
    row.SetEarnings(stock.ticker, stock.earnings);
    row.SetStockLine(stock);
    
    this.objPortfolioStocksNumber.innerHTML = this.PortfolioStocksCount;
    $('[data-toggle="tooltip"]').tooltip();
}

ModuleStockView.prototype.UpdateStocksPrice = function() {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": parseInt(this.PortfolioID),
        "portfolio_name": this.PortfolioName
    }, function(res) {
        var payload = res.data.payload;
        var portfolio = payload.portfolio;
        
        self.objPortfolioEarnings.innerHTML = portfolio.earnings;
        if (portfolio.earnings < 0) {
            self.objPortfolioEarnings.style.color = "RED";
        } else {
            self.objPortfolioEarnings.style.color = "GREEN";
        }

        self.RebuildPortfolioEarnings(payload.portfolio);
    });
}

ModuleStockView.prototype.GetStocks = function() {
    var self = this;

    this.PortfolioID            = 0;
    this.PortfolioName          = "All"
    this.PortfolioStocksCount   = 0;

    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": this.PortfolioID,
        "portfolio_name": this.PortfolioName
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