function StockMarket() {
    this.Stocks 		= {};
    this.MarketStatus 	= null;
    this.UpdateInterval	= 10000;
    this.DoWork 		= false;

    this.Callbacks 		= [];

    return this;
}

StockMarket.prototype.GetStockFromCache = function(ticker) {
    for (key in market.Stocks) {
        var stock = market.Stocks[key];
        if (stock.ticker == ticker) {
            return stock;
        }
    }
}

StockMarket.prototype.GetStocks = function() {
    var self = this;
    console.log("GetStocks");
    node.API.SendCustomCommand(NodeUUID, "get_market_stocks", {
    }, function(res) {
        var payload = res.data.payload;
        this.MarketStatus = payload.status;
        if (payload.status.local_stock_market_ready == false) {
            if (self.DoWork === true) {
                setTimeout(self.GetStocks.bind(self), 2500);
            }
            return;
        }
        if (self.DoWork === true) {
            setTimeout(self.GetStocks.bind(self), self.UpdateInterval);
        }
    });
}

StockMarket.prototype.GetPortfolioStatistics = function(portfolio_id, callback) {
    var self = this;
    console.log("GetPortfolioStatistics");
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_statistics", {
        "portfolio_id": portfolio_id
    }, function(res) {
        var payload = res.data.payload;
        callback(payload);
    });
}

StockMarket.prototype.Start = function() {
    console.log("StockMarket Start");
    this.DoWork = true;
    this.GetStocks();
}

StockMarket.prototype.Stop = function() {
    console.log("StockMarket Stop");
    this.DoWork = false;
}

StockMarket.prototype.Update = function() {
    this.GetStocks();
}

StockMarket.prototype.Publish = function(data) {
    console.log("Publish", data.length);
    for (key in data) {
        var stock = data[key];
        this.Stocks[stock.ticker] = stock;
    }

    for (key in this.Callbacks) {
        var handler  = this.Callbacks[key];
        handler.callback(data, handler.scope);
    }
}

StockMarket.prototype.DeleteStock = function(ticker) {
    delete this.Stocks[ticker];
}

StockMarket.prototype.Register = function(id, callback, scope) {
    this.Callbacks[id] = { 
        callback: callback,
        id: id,
        scope: scope
    };
}

StockMarket.prototype.Unregister = function(id) {
    delete self.Callbacks[id];
}