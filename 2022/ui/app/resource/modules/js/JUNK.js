/*

<div class="col-xl-12" id="id_m_stock_view_loader_ui">
    <div class="row">
        <div class="col-lg-12" style="text-align:center;">
            <h4>Loading...</h4>
        </div>
    </div>
</div>

<div class="col-xl-12">
    <div id="id_stocks_loading_progressbar"></div>
</div>

ModuleStockAppend.prototype.HideLoader = function() {
    var objLoader = document.getElementById("id_m_stock_view_loader_ui");
    if (objLoader !== undefined || objLoader !== null) {
        objLoader.classList.add("d-none");
    }
}

ModuleDashboardView.prototype.GetStocks = function() {
    var self = this;

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

        self.HideLoader();
        self.StockLoaderProgressBar.Hide();
    });
}
*/

 /* document.getElementById('d_m_stock_append_stock_find_ticker').addEventListener('keyup', function(event) {
    if (event.code === 'Enter') {
        event.preventDefault();
        self.FindStockInMarket(document.getElementById('d_m_stock_append_stock_find_ticker').value);
    }
}); */