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
    this.SelectedManagerFund        = "All";

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

        if (callback !== undefined && callback != null) {
            callback(self);
        }
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
        self.GetStockDistribution(funds_number_list);
        self.Funds = Array.from(payload.funds);
        
        // Update managers list
        mngrs = self.GetFunsManagersList(payload.funds);
        var objDropMngrs = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_mngrs");
        for (key in mngrs) {
            var obj = document.createElement("option");
            obj.text = mngrs[key];
            objDropMngrs.add(obj);
        }
    });
}

ModuleDashboardView.prototype.GetPortfolioFunds = function(id, name) {
    // GetFundsByPortfolio
    // UpdateFundsTable
    var self = this;

    if (id != 0) {
        node.API.SendCustomCommand(NodeUUID, "get_porfolio_funds", {
            "portfolio_id": id
        }, function(res) {
            var payload = res.data.payload;
            self.UpdateFundsTable(payload.funds);
        });
    } else {
        this.GetAllFunds();
    }
}

ModuleDashboardView.prototype.GetPortfolioList = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        var obj = document.getElementById("id_m_funder_dashboard_view_funds_table_portfolio_dropdown_items");

        self.PortfolioList = payload.portfolios;
        obj.innerHTML = `<span class="dropdown-item" style="cursor:pointer" onclick="window.DashboardView.GetPortfolioFunds(0,'All');">All</span>`;
        for (key in payload.portfolios) {
            item = payload.portfolios[key];
            obj.innerHTML += `<span class="dropdown-item" style="cursor:pointer" onclick="window.DashboardView.GetPortfolioFunds(`+item.id+`,'`+item.name+`');">`+item.name+`</span>`;
        }
    });
}

ModuleDashboardView.prototype.FundManagerSelectionChange = function() {
    var objDropMngrs = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_mngrs");
    this.SelectedManagerFund = objDropMngrs.value;
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
    this.GetPortfolioList();
    feather.replace();
}

ModuleDashboardView.prototype.Filter = function() {
    var self = this;
    var funds_number_list = []
    var funds = [];

    var objFeeLow = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_fee_low");
    var objFeeHigh = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_fee_high");

    for (key in this.Funds) {
        var fund = this.Funds[key];
        var isAppend    = false;
        var filterFee   = false;
        var filterMngr  = false;

        if (((objFeeLow.value !== "" && fund.fee >= parseFloat(objFeeLow.value)) || objFeeLow.value == "") && 
            ((objFeeHigh.value !== "" && fund.fee <= parseFloat(objFeeHigh.value)) || objFeeHigh.value == "")) {
            filterFee = true;
        }

        if (this.SelectedManagerFund == "All" || (this.SelectedManagerFund != "All" && fund.mngr == this.SelectedManagerFund)) {
            filterMngr = true;
        }

        if (filterFee & filterMngr) {
            isAppend = true;
        }

        if (isAppend == true) {
            funds_number_list.push(fund.number);
            funds.push(fund);
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

            var us_perc = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stock_perc").value;
            var is_perc = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stock_perc").value;
            var other_perc = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_other_stock_perc").value;

            console.log(payload);

            for (key in funds) {
                var fund = funds[key];
                for (idx in investment) {
                    var invest = investment[idx];
                    if (invest.number == fund.number) {
                        var us_filter = false;
                        var is_filter = false;
                        var other_filter = false;

                        // Check US holdings
                        if (objUsCheckbox.checked && (us_perc !== undefined && us_perc !== null && us_perc != "")) {
                            if (((invest.us_holdings / invest.holdings_count) * 100) >= parseInt(us_perc)) {
                                us_filter = true;
                            }
                        } else {
                            us_filter = true;
                        }
                        // Check IS holdings
                        if (objIsCheckbox.checked && (us_perc !== undefined && us_perc !== null && us_perc != "")) {
                            if (((invest.is_holdings / invest.holdings_count) * 100) >= parseInt(is_perc)) {
                                is_filter = true;
                            }
                        } else {
                            is_filter = true;
                        }
                        // Check Other holdings
                        if (objOtherCheckbox.checked && (us_perc !== undefined && us_perc !== null && us_perc != "")) {
                            if (((invest.other_holdings / invest.holdings_count) * 100) >= parseInt(other_perc)) {
                                other_filter = true;
                            }
                        } else {
                            other_filter = true;
                        }

                        if (us_filter & is_filter & other_filter) {
                            new_funds.push(fund);
                            new_funds_number_list.push(fund.number);
                            // Save index
                        } else {
                        }

                        break;
                    }
                    // Delete this item from investment
                }
            }

            if (new_funds.length > 0) {
                console.log("new_funds", new_funds.length);
                self.UpdateFundsTable(new_funds);
            } else {
                console.log("funds", funds.length);
                self.UpdateFundsTable(funds);
            }

            if (new_funds_number_list.length > 0) {
                console.log("new_funds_number_list", new_funds_number_list.length);
                self.GetStockDistribution(new_funds_number_list);
            } else {
                console.log("funds_number_list", funds_number_list.length);
                self.GetStockDistribution(funds_number_list);
            }
        });
    } else {
        this.UpdateFundsTable(funds);
        this.GetStockDistribution(funds_number_list);
    }
}

ModuleDashboardView.prototype.GetStockDistribution = function(funds) {
    node.API.SendCustomCommand(NodeUUID, "get_stock_distribution", {
        "funds": funds
    }, function(res) {
        var payload = res.data.payload;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks").style.width = ((payload.us / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks").innerHTML = ((payload.us / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_info").innerHTML = payload.us + " / " + payload.fund_stocks;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks").style.width = ((payload.is / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks").innerHTML = ((payload.is / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_info").innerHTML = payload.is + " / " + payload.fund_stocks;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks").style.width = ((payload.government / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks").innerHTML = ((payload.government / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks_info").innerHTML = payload.government + " / " + payload.fund_stocks;
        
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_all").style.width = ((payload.us / payload.all.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_all").innerHTML = ((payload.us / payload.all.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_all_info").innerHTML = payload.us + " / " + payload.all.all;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_all").style.width = ((payload.is / payload.all.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_all").innerHTML = ((payload.is / payload.all.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_all_info").innerHTML = payload.is + " / " + payload.all.all;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks_all").style.width = ((payload.government / payload.all.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks_all").innerHTML = ((payload.government / payload.all.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks_all_info").innerHTML = payload.government + " / " + payload.all.all;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_ratio").style.width = ((payload.us / payload.all.us) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_ratio").innerHTML = ((payload.us / payload.all.us) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_ratio_info").innerHTML = payload.us + " / " + payload.all.us;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_ratio").style.width = ((payload.is / payload.all.is) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_ratio").innerHTML = ((payload.is / payload.all.is) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_ratio_info").innerHTML = payload.is + " / " + payload.all.is;

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_other_stocks_ratio").style.width = ((payload.government / payload.all.other) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_other_stocks_ratio").innerHTML = ((payload.government / payload.all.other) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_other_stocks_ratio_info").innerHTML = payload.government + " / " + payload.all.other;
    });
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