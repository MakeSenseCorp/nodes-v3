function ModuleStocksAdaptor() {
    var self = this;
    return this;
}

ModuleStocksAdaptor.prototype.GetPotrfolioStocks = function(id, name, callback) {
    node.API.SendCustomCommand(NodeUUID, "get_portfolio_stocks", {
        "portfolio_id": id,
        "portfolio_name": name
    }, function(res) {
        var payload = res.data.payload;
        if (payload.status.local_stock_market_ready == false) {
            callback(null);
        } else {
            callback(payload);
        }
    });
}

ModuleStocksAdaptor.prototype.GetPotrfolioStocks = function(callback) {
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        callback(payload.portfolios);
    });
}

ModuleStocksAdaptor.prototype.GetDataBaseStocks = function(callback) {
    node.API.SendCustomCommand(NodeUUID, "get_db_stocks", {
    }, function(res) {
        var payload = res.data.payload;
        callback(payload.stocks);
    });
}

