function ModulePortfolioSelectorView(fund_id) {
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
                                            <input type="checkbox" class="custom-control-input" onclick="[DOM].SetFundPortfolio(this,[PORTFOLIO_ID]);" id="id_portfolio_fund_list_[PORTFOLIO_ID]">
                                            <label class="custom-control-label" for="id_portfolio_fund_list_[PORTFOLIO_ID]">[PORTFOLIO_NAME]</label>
                                        </div>
                                    `;
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;
    this.PortfolioList              = [];
    this.MyPortfolios               = [];
    this.FundID                     = fund_id;

    return this;
}

ModulePortfolioSelectorView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModulePortfolioSelectorView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModulePortfolioSelectorView.prototype.SetFundPortfolio = function(obj, id) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "set_fund_portfolios", {
        "portfolio_id": id,
        "status": obj.checked,
        "fund_id": self.FundID
    }, function(res) {
        var payload = res.data.payload;
    });
}

ModulePortfolioSelectorView.prototype.GetFundPortfolios = function(fund_id) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_fund_portfolios", {
        "fund_id": fund_id
    }, function(res) {
        var payload = res.data.payload;
        self.MyPortfolios = payload.portfolios;
        for (key in self.PortfolioList) {
            portfolio = self.PortfolioList[key];
            obj = document.getElementById("id_portfolio_fund_list_"+portfolio.id);
            obj.checked = self.MyPortfolios.includes(portfolio.id);
        }
    });
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

        self.GetFundPortfolios(self.FundID);
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