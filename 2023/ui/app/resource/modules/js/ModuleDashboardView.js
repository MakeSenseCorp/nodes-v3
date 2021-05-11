function ModuleDashboardView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;
    this.FundInfoModule             = null;
    this.Funds                      = null;
    this.FilteredFunds              = null;
    this.SelectedManagerFund        = "All";

    this.FeeSlider                  = null;
    this.USPercentSlider            = null;
    this.ISPercentSlider            = null;
    this.OtherPercentSlider         = null;
    this.DistributionView           = null;
    this.PortfolioDropDown          = null;
    this.FundMngrDropDown           = null;

    return this;
}

ModuleDashboardView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleDashboardView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleDashboardView.prototype.TableUIChangeEvent = function() {
    feather.replace();
}

ModuleDashboardView.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleDashboardView.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        self.ComponentObject = document.getElementById("id_m_funder_dashboard_view_"+this.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;

        self.FeeSlider = new MksMultiRangeSlider({
            min: 0,
            max: 5,
            step: 0.1,
            left: 0,
            right: 5
        });
        self.FeeSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_fee"));
        self.USPercentSlider = new MksMultiRangeSlider({
            min: 0,
            max: 100,
            step: 1,
            left: 0,
            right: 100
        });
        self.USPercentSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_us_perc"));
        self.ISPercentSlider = new MksMultiRangeSlider({
            min: 0,
            max: 100,
            step: 1,
            left: 0,
            right: 100
        });
        self.ISPercentSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_is_perc"));
        self.OtherPercentSlider = new MksMultiRangeSlider({
            min: 0,
            max: 100,
            step: 1,
            left: 0,
            right: 100
        });
        self.OtherPercentSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_other_perc"));

        self.DistributionView = new ModuleDistributionView({
            portfolio: {
                enabled: true
            },
            total: {
                enabled: true
            },
            ratio: {
                enabled: true
            },
        });
        self.DistributionView.SetObjectDOMName("distribution");
        self.DistributionView.SetHostingID("id_m_funder_dashboard_view_funds_table_filter");
        self.DistributionView.Build(null, null);

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleDashboardView.prototype.OptimizeCallback = function(payload) {
    var numbers = payload.funds;
    var funds_list = null;
    var funds = [];

    this.DistributionView.GetStockDistribution(numbers);

    if (this.FilteredFunds.length != 0) {
        funds_list = this.FilteredFunds;
    } else {
        funds_list = this.Funds;
    }

    for (key in funds_list) {
        var fund = funds_list[key];
        if (numbers.indexOf(fund.number) > 0) {
            funds.push(fund);
        }
    }

    this.UpdateFundsTable(funds);
    this.FilteredFunds = Array.from(funds);
    window.Modal.Hide();
}

ModuleDashboardView.prototype.Optimize = function() {
    var funds_list = null;
    var funds_number_list = [];

    var perc1 = document.getElementById("id_m_funder_dashboard_view_funds_stock_threshold").value;
    var perc2 = document.getElementById("id_m_funder_dashboard_view_funds_success_threshold").value;

    console.log(perc1, perc2);

    if (this.FilteredFunds.length != 0) {
        funds_list = this.FilteredFunds;
    } else {
        funds_list = this.Funds;
    }

    if (funds_list.length == 0) {
        return;
    }

    for (key in funds_list) {
        var fund = funds_list[key];
        funds_number_list.push(fund.number);
    }

    if (funds_list.length > 0) {
        node.API.SendCustomCommand(NodeUUID, "optimize", {
            "fund_number_list": funds_number_list,
            "perc": parseInt(perc1),
            "perc2": parseInt(perc2)
        }, function(res) {
            var payload = res.data.payload;
            document.getElementById("modal_optimize_run").classList.add("d-none");
        });
    }
}

ModuleDashboardView.prototype.OpenOptimizeModal = function() {
    window.Modal.Remove();
    window.Modal.SetTitle("Optimize");
    window.Modal.SetContent(`
        <form>
            <div class="form-group row">
                <div class="col-sm-8">
                    <label for="id_m_funder_dashboard_view_funds_stock_threshold" class="col-sm-8 col-form-label">Stock (%)</label>
                </div>
                <div class="col-sm-4">
                    <input type="text" class="form-control" id="id_m_funder_dashboard_view_funds_stock_threshold" value="40">
                </div>
            </div>
            <div class="form-group row">
                <div class="col-sm-8">
                    <label for="id_m_funder_dashboard_view_funds_success_threshold" class="col-sm-8 col-form-label">Success (%)</label>
                </div>
                <div class="col-sm-4">
                    <input type="text" class="form-control" id="id_m_funder_dashboard_view_funds_success_threshold" value="90">
                </div>
            </div>
        </form>
    `);
    window.Modal.SetFooter(`<button type="button" id="modal_optimize_run" class="btn btn-success" onclick="window.DashboardView.Optimize();">Run</button><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
    window.Modal.Build("sm");
    window.Modal.Show();
}

ModuleDashboardView.prototype.OpenPortfoliosModal = function() {
    var self = this;

    window.PortfoliosView = new ModulePortfolioView();
    window.PortfoliosView.SetObjectDOMName("window.PortfoliosView");

    window.PortfoliosView.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Stocks");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("lg");
        window.Modal.Show();

        module.UpdatePortfolioList();
    });
}

ModuleDashboardView.prototype.OpenStocksModal = function() {
    var self = this;

    window.StocksView = new ModuleStocksView();
    window.StocksView.SetObjectDOMName("window.StocksView")

    window.StocksView.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Stocks");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("lg");
        window.Modal.Show();

        var funds_number_list = [];
        if (self.FilteredFunds.length != 0) {
            funds_list = self.FilteredFunds;
        } else {
            funds_list = self.Funds;
        }

        for (key in funds_list) {
            var fund = funds_list[key]
            funds_number_list.push(fund.number);
        }

        module.Initiate();
        module.GetStocksRate(funds_number_list);
    });
}

ModuleDashboardView.prototype.OpenFundInfoModal = function(number) {
    this.FundInfoModule = new ModuleFundInfoView(number);
    this.FundInfoModule.SetObjectDOMName(this.DOMName+".FundInfoModule");
    this.FundInfoModule.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Fund Information");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("lg");
        window.Modal.Show();
        module.GetAllFundInfo();
    });
}

ModuleDashboardView.prototype.GetAllFunds = function() {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "get_all_funds", {
    }, function(res) {
        var payload = res.data.payload;
        var funds = [];
        var funds_number_list = []

        for (key in payload.funds) {
            fund = payload.funds[key];           
            funds.push(fund);
            funds_number_list.push(fund.number);
        }
        self.UpdateFundsTable(funds);
        self.DistributionView.GetStockDistribution(funds_number_list);
        self.Funds = Array.from(payload.funds);
        
        // Update managers list
        mngrs = self.GetFunsManagersList(payload.funds);
        self.FundMngrDropDown = new MksBasicDropDown();
        self.FundMngrDropDown.Build(document.getElementById("id_m_funder_dashboard_view_funds_table_filter_mngrs_dropdown"));
        self.FundMngrDropDown.UpdateSelected("Fund Managers");
        self.FundMngrDropDown.AppendItem({
            name: "All",
            onclick: "window.DashboardView.SelectManager('All');"
        });
        for (key in mngrs) {
            self.FundMngrDropDown.AppendItem({
                name: mngrs[key],
                onclick: `window.DashboardView.SelectManager('`+mngrs[key]+`');`
            })
        }
        self.FilteredFunds = [];
        self.GetPortfolioList();
    });
}

ModuleDashboardView.prototype.SelectManager = function(name) {
    var funds_list = null;
    this.SelectedManagerFund = name;
    var funds_number_list = []

    if (name == "All") {
        this.FundMngrDropDown.UpdateSelected("Fund Managers");
    } else {
        this.FundMngrDropDown.UpdateSelected(name);
    }

    if (this.FilteredFunds.length != 0) {
        funds_list = this.FilteredFunds;
    } else {
        funds_list = this.Funds;
    }

    this.FilteredFunds = [];
    for (key in funds_list) {
        var fund = funds_list[key]
        if (this.SelectedManagerFund == "All" || (this.SelectedManagerFund != "All" && fund.mngr == this.SelectedManagerFund)) {
            funds_number_list.push(fund.number);
            this.FilteredFunds.push(fund);
        }
    }

    this.UpdateFundsTable(this.FilteredFunds);
    this.DistributionView.GetStockDistribution(funds_number_list);
}

ModuleDashboardView.prototype.OpenCreatePortfolioModal = function() {
    window.Modal.Remove();
    window.Modal.SetTitle("Create Portfolio");
    window.Modal.SetContent(`
        <div class="row">
            <div class="col-md-12">
                <input type="text" class="form-control form-control-sm" id="id_m_funder_dashboard_view_funds_create_portfolio_name" placeholder="Name">
            </div>
        </div>
    `);
    window.Modal.SetFooter(`<button type="button" class="btn btn-success" onclick="window.DashboardView.CreatePortfolio();">Create</button><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
    window.Modal.Build("sm");
    window.Modal.Show();
}

ModuleDashboardView.prototype.CreatePortfolio = function() {
    var self = this;
    var funds_list = null;
    var portfolio_name = "";
    var objName = document.getElementById("id_m_funder_dashboard_view_funds_create_portfolio_name");

    if (objName === undefined || objName === null) {
        return;
    }

    if (objName.value == "") {
        return;
    }

    if (this.FilteredFunds.length != 0) {
        funds_list = this.FilteredFunds;
    } else {
        funds_list = this.Funds;
    }

    if (funds_list.length == 0) {
        return;
    }

    node.API.SendCustomCommand(NodeUUID, "create_portfolio_from_list", {
        "name": objName.value,
        "funds": funds_list
    }, function(res) {
        var payload = res.data.payload;
        window.Modal.Hide();
    });
}

ModuleDashboardView.prototype.GetPortfolioFunds = function(id, name) {
    var self = this;

    if (id != 0) {
        node.API.SendCustomCommand(NodeUUID, "get_porfolio_funds", {
            "portfolio_id": id
        }, function(res) {
            var payload = res.data.payload;
            var funds_number_list = [];
            self.FilteredFunds = [];
            self.UpdateFundsTable(payload.funds);

            for (key in payload.funds) {
                var fund = payload.funds[key];
                funds_number_list.push(fund.number);
            }
            self.DistributionView.GetStockDistribution(funds_number_list);
            self.Funds = Array.from(payload.funds);
            self.PortfolioDropDown.UpdateSelected(name);
        });
    } else {
        this.GetAllFunds();
    }
}

ModuleDashboardView.prototype.GetPortfolioList = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        self.PortfolioDropDown = new MksBasicDropDown();
        self.PortfolioDropDown.Build(document.getElementById("id_m_funder_dashboard_view_funds_table_portfolio_dropdown"));

        self.PortfolioList = payload.portfolios;
        self.PortfolioDropDown.UpdateSelected("All");
        self.PortfolioDropDown.AppendItem({
            name: "All",
            onclick: "window.DashboardView.GetPortfolioFunds(0,'All');"
        });
        for (key in payload.portfolios) {
            item = payload.portfolios[key];
            self.PortfolioDropDown.AppendItem({
                name: item.name,
                onclick: `window.DashboardView.GetPortfolioFunds(`+item.id+`,'`+item.name+`');`
            });
        }
    });
}

ModuleDashboardView.prototype.UpdateFundsTable = function(funds_list) {
    var data  = [];
    var table = new MksBasicTable();

    table.EnableListing();
    table.SetListingWindowSize(15);
    table.RegisterUIChangeEvent(this.TableUIChangeEvent);
    table.SetSchema(["", "", "", "", "", "", "", "", "", "", "", "", ""]);

    for (key in funds_list) {
        var fund = funds_list[key];
        var row = [];
        var color = "black";

        row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer" onclick="window.DashboardView.OpenFundInfoModal(`+fund.number+`)">`+fund.number+`</a></h6>`);
        row.push(`<span>`+fund.name+`</span>`);
        row.push(`<span>`+fund.mngr+`</span>`);
        row.push(`<span>`+fund.ivest_mngr+`</span>`);
        if (fund.d_change < 0) {
            color = "red";
        } else {
            color = "green";
        }
        row.push(`<span style="color:`+color+`">`+fund.d_change+`</span>`);
        row.push(`<span>`+fund.month_begin+`</span>`);
        if (fund.y_change < 0) {
            color = "red";
        } else {
            color = "green";
        }
        row.push(`<span style="color:`+color+`">`+fund.y_change+`</span>`);
        row.push(`<span>`+fund.year_begin+`</span>`);
        if (fund.fee > 0.8) {
            color = "red";
        } else {
            color = "green";
        }
        row.push(`<span style="color:`+color+`">`+fund.fee+`</span>`);
        row.push(`<span>`+fund.fund_size+`</span>`);
        row.push(`<span>`+fund.last_updated+`</span>`);
        row.push(`<span>`+fund.mimic+`</span>`);
        row.push(`
            <div class="d-flex flex-row-reverse">
                <div class="dropdown">
                    <button class="btn btn-outline-secondary dropdown-toggle btn-sm" type="button" id="id_m_stock_append_stock_dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        <span data-feather="menu"></span>
                    </button>
                    <div class="dropdown-menu text-center" aria-labelledby="id_m_stock_append_stock_dropdown">
                        <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+this.DOMName+`.OpenPortfolioSelectorModal(`+fund.id+`);">Portfolios</span>
                        <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="">Settings</span>
                    </div>
                </div>
            </div>
        `);
        data.push(row);
    }

    table.ShowRowNumber(false);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_funder_dashboard_view_funds_table"));
    feather.replace();
}

ModuleDashboardView.prototype.Filter = function() {
    var self = this;
    var funds_number_list = []
    var funds = [];
    var funds_list = null;

    var objFeeLow  = this.FeeSlider.GetValue()[0];
    var objFeeHigh = this.FeeSlider.GetValue()[1];

    var objUsCheckbox    = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_fund_fee_check");

    if (this.FilteredFunds.length != 0) {
        funds_list = this.FilteredFunds;
    } else {
        funds_list = this.Funds;
    }

    this.FilteredFunds = [];
    for (key in funds_list) {
        var fund = funds_list[key];
        var isAppend    = false;
        var filterFee   = false;
        var filterName  = false;

        if (objUsCheckbox.checked) {
            if (((fund.fee >= parseFloat(objFeeLow)) || objFeeLow == "") && 
                ((fund.fee <= parseFloat(objFeeHigh)) || objFeeHigh == "")) {
                filterFee = true;
            }
        } else {
            filterFee = true;
        }

        var name = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_name").value;
        if (name == "") {
            filterName = true;
        } else {
            if (fund.name.includes(name)) {
                filterName = true;
            }
        }

        if (filterFee & filterName) {
            isAppend = true;
        }

        if (isAppend == true) {
            funds_number_list.push(fund.number);
            funds.push(fund);
            this.FilteredFunds.push(fund);
        }
    }

    var objUsCheckbox    = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stock_perc_check");
    var objIsCheckbox    = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stock_perc_check");
    var objOtherCheckbox = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_other_stock_perc_check");
    
    if (objUsCheckbox.checked == true || objIsCheckbox.checked == true || objOtherCheckbox.checked == true) {
        node.API.SendCustomCommand(NodeUUID, "get_stock_investment", {
            "funds": funds_number_list
        }, function(res) {
            var payload = res.data.payload;
            var investment = payload.investment;
            var new_funds_number_list = [];
            var new_funds = [];
            self.FilteredFunds = [];

            var us_perc = self.USPercentSlider.GetValue();
            var is_perc = self.ISPercentSlider.GetValue();
            var other_perc = self.OtherPercentSlider.GetValue();

            for (key in funds) {
                var fund = funds[key];
                for (idx in investment) {
                    var invest = investment[idx];
                    if (invest.number == fund.number) {
                        var us_filter = false;
                        var is_filter = false;
                        var other_filter = false;

                        // Check US holdings
                        if (objUsCheckbox.checked) {
                            if (parseInt(invest.holdings_count) > 0) {
                                if (((invest.us_holdings / invest.holdings_count) * 100) >= parseInt(us_perc[0]) && ((invest.us_holdings / invest.holdings_count) * 100) <= parseInt(us_perc[1])) {
                                    us_filter = true;
                                }
                            }
                        } else {
                            us_filter = true;
                        }
                        // Check IS holdings
                        if (objIsCheckbox.checked) {
                            if (parseInt(invest.holdings_count) > 0) {
                                if (((invest.is_holdings / invest.holdings_count) * 100) >= parseInt(is_perc[0]) && ((invest.is_holdings / invest.holdings_count) * 100) <= parseInt(is_perc[1])) {
                                    is_filter = true;
                                }
                            }
                        } else {
                            is_filter = true;
                        }
                        // Check Other holdings
                        if (objOtherCheckbox.checked) {
                            if (parseInt(invest.holdings_count) > 0) {
                                if (((invest.other_holdings / invest.holdings_count) * 100) >= parseInt(other_perc[0]) && ((invest.other_holdings / invest.holdings_count) * 100) <= parseInt(other_perc[1])) {
                                    other_filter = true;
                                }
                            }
                        } else {
                            other_filter = true;
                        }

                        if (us_filter & is_filter & other_filter) {
                            new_funds.push(fund);
                            new_funds_number_list.push(fund.number);
                            self.FilteredFunds.push(fund);
                            // Save index
                        } else {
                        }

                        break;
                    }
                    // Delete this item from investment
                }
            }

            if (new_funds.length > 0) {
                self.UpdateFundsTable(new_funds);
            } else {
                self.UpdateFundsTable([]);
            }

            if (new_funds_number_list.length > 0) {
                self.DistributionView.GetStockDistribution(new_funds_number_list);
            } else {
                self.DistributionView.GetStockDistribution([]);
            }
        });
    } else {
        this.UpdateFundsTable(funds);
        this.DistributionView.GetStockDistribution(funds_number_list);
    }
}

ModuleDashboardView.prototype.GetFunsManagersList = function(funds) {
    var mngrs = []
    for (key in funds) {
        fund = funds[key];
        if (mngrs.includes(fund.mngr) == false) {
            mngrs.push(fund.mngr);
        }
    }

    return mngrs;
}

ModuleDashboardView.prototype.OpenPortfolioSelectorModal = function(fund_id) {
    this.Selector = new ModulePortfolioSelectorView(fund_id);
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

ModuleDashboardView.prototype.Clean = function() {
    clearInterval(this.GetStocksTimerHndl);
}

ModuleDashboardView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleDashboardView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}