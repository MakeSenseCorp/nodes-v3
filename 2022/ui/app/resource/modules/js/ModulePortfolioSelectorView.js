function ModulePortfolioSelectorView(ticker) {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.DOMName                    = "";
    this.MainView                   = `
                                        <div class="row">
                                            <div class="col-sm-12">[PORTFOLIOS]</div>
                                        </div>`;
    this.PortofoliosCheckbox        = `
                                        <div class="custom-control custom-checkbox">
                                            <input type="checkbox" class="custom-control-input" onclick="[DOM].AppendStockToPortfolio(this,'[TICKER]','[PORTFOLIO_ID]');" id="id_portfolio_stock_list_[PORTFOLIO_ID]">
                                            <label class="custom-control-label" for="id_portfolio_stock_list_[PORTFOLIO_ID]">[PORTFOLIO_NAME]</label>
                                        </div>
                                    `;
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;
    this.PortfolioList              = [];
    this.Ticker                     = ticker;

    return this;
}

ModulePortfolioSelectorView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModulePortfolioSelectorView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModulePortfolioSelectorView.prototype.AppendStockToPortfolio = function(obj, ticker, portfolio_id) {
    console.log(ticker, portfolio_id);
}

ModulePortfolioSelectorView.prototype.Build = function(data, callback) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        self.PortfolioList = payload.portfolios;
        self.HTML = self.MainView;
        portfolioCheckboxes = "";
        for (key in payload.portfolios) {
            item = payload.portfolios[key];
            html = self.PortofoliosCheckbox;
            html = html.split("[PORTFOLIO_NAME]").join(item.name);
            html = html.split("[PORTFOLIO_ID]").join(item.id);
            html = html.split("[DOM]").join(self.DOMName);
            html = html.split("[TICKER]").join(self.Ticker);
            portfolioCheckboxes += html;
        }
        self.HTML = self.HTML.split("[PORTFOLIOS]").join(portfolioCheckboxes);

        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            self.HostingObject.innerHTML = self.HTML;
        }

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModulePortfolioSelectorView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModulePortfolioSelectorView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}