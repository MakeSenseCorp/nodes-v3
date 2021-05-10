function ModuleDistributionView(conf) {
    var self = this;

    // Modules basic
    this.HTML 	                    = `
        <div class="row justify-content-xl-center">
            <div class="col-xl-2"></div>
            <div class="col-xl-3 text-center">
                <strong><span>US Stocks (%)</span></strong>
            </div>
            <div class="col-xl-3 text-center">
                <strong><span>IS Stocks (%)</span></strong>
            </div>
            <div class="col-xl-3 text-center">
                <strong><span>Other Holdings (%)</span></strong>
            </div>
            <div class="col-xl-1"></div>
        </div>
        <br>
    `;
    this.ID                         = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    this.HTMLComponentStock         = `
        <div class="row justify-content-xl-center">
            <div class="col-xl-2"><strong><span>[NAME]</span></strong></div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_us_stocks_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_us_stocks_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_is_stocks_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_is_stocks_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_government_stocks_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_government_stocks_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-1"></div>
        </div>
        <br>
    `;
    this.HTMLComponentAll            = `
        <div class="row justify-content-xl-center">
            <div class="col-xl-2"><strong><span>[NAME]</span></strong></div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_us_stocks_all_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_us_stocks_all_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_is_stocks_all_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_is_stocks_all_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_government_stocks_all_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_government_stocks_all_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-1"></div>
        </div>
        <br>
    `;
    this.HTMLComponentRatio         = `
        <div class="row justify-content-xl-center">
            <div class="col-xl-2"><strong><span>[NAME]</span></strong></div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_us_stocks_ratio_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_us_stocks_ratio_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_is_stocks_ratio_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_is_stocks_ratio_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-3">
                <div class="progress">
                    <div class="progress-bar bg-success" id="id_m_funder_dashboard_view_funds_table_filter_other_stocks_ratio_[MODULE_NAME]" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <span id="id_m_funder_dashboard_view_funds_table_filter_other_stocks_ratio_[MODULE_NAME]_info"></span>
            </div>
            <div class="col-xl-1"></div>
        </div>
        <br>
    `;
    this.Config                     = conf;
    // Objects section
    this.ComponentObject            = null;

    return this;
}

ModuleDistributionView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleDistributionView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
    this.ID = this.HostingID+"_"+this.Name;
}

ModuleDistributionView.prototype.Build = function(data, callback) {
    var self = this;
    var html = this.HTML;

    if (this.Config.portfolio.enabled) {
        html += this.HTMLComponentStock.split("[NAME]").join("Portfolio");
        html = html.split("[MODULE_NAME]").join(this.DOMName);
    }

    if (this.Config.total.enabled) {
        html += this.HTMLComponentAll.split("[NAME]").join("Total");
        html = html.split("[MODULE_NAME]").join(this.DOMName);
    }

    if (this.Config.ratio.enabled) {
        html += this.HTMLComponentRatio.split("[NAME]").join("Ratio");
        html = html.split("[MODULE_NAME]").join(this.DOMName);
    }

    // this.ComponentObject = document.getElementById(this.ID);

    document.getElementById(this.HostingID).innerHTML = html;

    if (callback !== undefined && callback != null) {
        callback(this);
    }
}

ModuleDistributionView.prototype.UpdateFilterDistributionUI = function(id, a, b) {
    var perc = "0%";

    if (b != 0) {
        perc = ((a / b) * 100).toFixed(2) + "%";
    }

    document.getElementById(id).style.width = perc;
    document.getElementById(id).innerHTML = perc;
    document.getElementById(id+"_info").innerHTML = a + " / " + b;
}

ModuleDistributionView.prototype.GetStockDistribution = function(funds) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_stock_distribution", {
        "funds": funds
    }, function(res) {
        var payload = res.data.payload;

        var portfolio_stocks_count = 0;
        if (payload.fund_stocks != 0) {
            portfolio_stocks_count = payload.fund_stocks;
        }
        
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_us_stocks_"+self.DOMName, payload.us, payload.fund_stocks);
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_is_stocks_"+self.DOMName, payload.is, payload.fund_stocks);
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_government_stocks_"+self.DOMName, payload.government, payload.fund_stocks);
        
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_us_stocks_all_"+self.DOMName, payload.us, payload.all.all);
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_is_stocks_all_"+self.DOMName, payload.is, payload.all.all);
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_government_stocks_all_"+self.DOMName, payload.government, payload.all.all);

        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_us_stocks_ratio_"+self.DOMName, payload.us, payload.all.us);
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_is_stocks_ratio_"+self.DOMName, payload.is, payload.all.is);
        self.UpdateFilterDistributionUI("id_m_funder_dashboard_view_funds_table_filter_other_stocks_ratio_"+self.DOMName, payload.government, payload.all.other);
    });
}

ModuleDistributionView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleDistributionView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}