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
    var objFee = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_fee");
    var funds_number_list = []
    var funds = [];
    for (key in this.Funds) {
        var fund = this.Funds[key];
        var isAppend    = false;
        var filterFee   = false;
        var filterMngr  = false;

        if ((objFee.value !== "" && fund.fee <= parseFloat(objFee.value)) || objFee.value == "") {
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
    
    if (objUsCheckbox.checked == true || objIsCheckbox.checked == true || objUsCheckbox.checked == true) {
        node.API.SendCustomCommand(NodeUUID, "get_stock_investment", {
            "funds": funds_number_list
        }, function(res) {
            var payload = res.data.payload;
            var investment = payload.investment;
            var funds_number_list = [];
            var new_funds = [];

            var us_perc = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stock_perc").value;
            console.log("get_stock_investment", payload.investment.length, us_perc);

            for (key in funds) {
                var fund = funds[key];
                for (idx in investment) {
                    var invest = investment[idx];
                    if (invest.number == fund.number) {
                        if (((invest.us_holdings / invest.holdings_count) * 100) > parseInt(us_perc)) {
                            funds_number_list.push(fund.number);
                            new_funds.push(fund);
                            // Save index
                        }
                        break;
                    }
                    // Delete this item from investment
                }
            }

            self.UpdateFundsTable(new_funds);
            self.GetStockDistribution(funds_number_list);
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

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks").innerHTML = ((payload.us / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks").innerHTML = ((payload.is / payload.fund_stocks) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks").innerHTML = ((payload.government / payload.fund_stocks) * 100).toFixed(2) + "%";

        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stocks_all").innerHTML = ((payload.us / payload.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stocks_all").innerHTML = ((payload.is / payload.all) * 100).toFixed(2) + "%";
        document.getElementById("id_m_funder_dashboard_view_funds_table_filter_government_stocks_all").innerHTML = ((payload.government / payload.all) * 100).toFixed(2) + "%";
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