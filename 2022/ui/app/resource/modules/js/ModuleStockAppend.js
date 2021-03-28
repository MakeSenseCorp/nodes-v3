function ModuleStockAppend() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.DOMName                    = "";
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;
    this.StockGraph                 = null;
    this.Selector                   = null;
    this.PortfolioList              = null;
    this.StockLoaderProgressBar	    = null;
    // Portfolio
    this.PortfolioID 	            = 0;
    this.PortfolioName              = "All";
    this.Earnings                   = 0.0;
    this.Number                     = 0;
    this.ModalDelete                = new MksBasicModal("m_stock_append_delete");

    return this;
}

ModuleStockAppend.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockAppend.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStockAppend.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleStockAppend.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);

        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            self.HostingObject.innerHTML = self.HTML;
        }

        /*
        self.StockLoaderProgressBar	= new MksBasicProgressBar("StockLoaderProgressBar");
        self.StockLoaderProgressBar.EnableInnerPercentageText(false);
        self.StockLoaderProgressBar.Build(document.getElementById("id_stocks_loading_progressbar"));
        self.StockLoaderProgressBar.Show();
        */
       
        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

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

ModuleStockAppend.prototype.OpenActionAppendModal = function (ticker, action) {
    var self = this;

    console.log("OpenActionAppendModal");

    window.Action = new ModuleAction();
    window.Action.SetObjectDOMName("window.Action");
    window.Action.SetHostingID("module_action");
    window.Action.Build({
        "ticker": ticker,
        "action": action
    }, null);

    var footer = `
        <button type="button" class="btn [COLOR]" onclick="[FUNC]">[NAME]</button>
        <button type="button" class="btn btn-secondary" data-dismiss="modal">No</button>
    `;
    footer = footer.split("[NAME]").join(action);
    if (action == "SELL") {
        footer = footer.split("[COLOR]").join("btn-success");
        footer = footer.split("[FUNC]").join("window.Action.AppendStockAction('"+ticker+"',1);");
    } else {
        footer = footer.split("[COLOR]").join("btn-danger");
        footer = footer.split("[FUNC]").join("window.Action.AppendStockAction('"+ticker+"',-1);");
    }

    window.Modal.Remove();
    window.Modal.SetTitle(action);
    window.Modal.SetContent(window.Action.HTML);
    window.Modal.SetFooter(footer);
    window.Modal.Build("lg");
    window.Modal.Show();
}

ModuleStockAppend.prototype.OpenStockActionsHistoryModal = function (ticker) {
    var self = this;

    console.log("OpenStockActionsHistoryModal");

    window.StockDetails = new ModuleStockDetails();
    window.StockDetails.SetHostingID("details_modal");
    window.StockDetails.SetObjectDOMName("window.StockDetails");
    window.StockDetails.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Details");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("lg");
        window.Modal.Show();
        module.GetDetails(ticker);
    });
}

ModuleStockAppend.prototype.GetPortfolioStocks = function(id, name) {
    console.log(id, name);

    this.Earnings   = 0.0;
    this.Number     = 0;
    
    var table = new MksBasicTable();
        table.SetSchema(["", "", "", "", "", "", ""]);
        var data = [];
        for (key in market.Stocks) {
            stock = market.Stocks[key];
            if (stock.portfolio_id == id || id == 0) {
                this.Earnings   += stock.earnings;
                this.Number     += stock.number;
                
                row = [];
                row.push(`<h6 class="my-0"><a href="#" onclick="`+this.DOMName+`.UpdateStockInfoView('`+stock.ticker+`');">`+stock.ticker+`</a></h6>`);
                row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_market_price">`+stock.market_price+`<span>`);
                row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_number">`+stock.number+`<span>`);
                row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_earnings">`+stock.earnings+`<span>`);
                row.push(`<span><span>`);
                row.push(`<span><span>`);
                row.push(`
                    <div class="d-flex flex-row-reverse">
                        <div class="dropdown">
                            <button class="btn btn-outline-secondary dropdown-toggle btn-sm" type="button" id="id_m_stock_append_stock_dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                <span data-feather="menu"></span>
                            </button>
                            <div class="dropdown-menu text-center" aria-labelledby="id_m_stock_append_stock_dropdown">
                                <span class="dropdown-item" style="color: RED; cursor:pointer; font-size: 12px;" onclick="`+this.DOMName+`.OpenActionAppendModal('`+stock.ticker+`','BUY');">Buy</span>
                                <span class="dropdown-item" style="color: GREEN; cursor:pointer; font-size: 12px;" onclick="`+this.DOMName+`.OpenActionAppendModal('`+stock.ticker+`','SELL');">Sell</span>
                                <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+this.DOMName+`.OpenStockActionsHistoryModal('`+stock.ticker+`');">History</span>
                                <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+this.DOMName+`.OpenPortfolioSelectorModal('`+stock.ticker+`');">Portfolios</span>
                                <span class="dropdown-item" style="color: RED; cursor:pointer; font-size: 12px;" onclick="`+this.DOMName+`.DeleteStock('`+stock.ticker+`');">Delete</span>
                            </div>
                        </div>
                    </div>
                `);
                data.push(row);
            }
        }
        table.ShowRowNumber(false);
        table.ShowHeader(false);
        table.SetData(data);
        table.AppendSummary([`<h6 style="color: BLUE">Overall</h6>`, "", `<span id="id_m_stock_append_table_price_summery_number" style="color: BLUE">`+this.Number+`<span>`, `<span id="id_m_stock_append_table_price_summery_earnings" style="color: BLUE">`+this.Earnings.toFixed(2)+`<span>`, "", "", ""])
        table.Build(document.getElementById("id_m_stock_append_stock_table"));
        feather.replace();
}

ModuleStockAppend.prototype.GetPortfolioList = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_portfolios", {}, function(res) {
        var payload = res.data.payload;
        var obj = document.getElementById("id_m_stock_append_portfolio_dropdown_items");

        self.PortfolioList = payload.portfolios;
        obj.innerHTML = `<span class="dropdown-item" style="cursor:pointer" onclick="window.StockAppend.GetPortfolioStocks(0,'All');">All</span>`;
        for (key in payload.portfolios) {
            item = payload.portfolios[key];
            obj.innerHTML += `<span class="dropdown-item" style="cursor:pointer" onclick="window.StockAppend.GetPortfolioStocks(`+item.id+`,'`+item.name+`');">`+item.name+`</span>`;
        }
    });
}

ModuleStockAppend.prototype.ShowStockAppendCheckbox = function(obj) {
    if (obj.checked == true) {
        document.getElementById("id_m_stock_append_stock_table").classList.remove("d-none");
    } else {
        document.getElementById("id_m_stock_append_stock_table").classList.add("d-none");
    }
}

ModuleStockAppend.prototype.AppendStock = function() {
    var self = this;
    var ticker = document.getElementById('d_m_stock_append_stock_find_ticker').value;
    node.API.SendCustomCommand(NodeUUID, "db_insert_stock", {
        'ticker': ticker
    }, function(res) {
        var payload = res.data.payload;
        self.GetDataBaseStocks();
    });
}

ModuleStockAppend.prototype.CleanModal = function() {
    this.ModalDelete.Remove();
}

ModuleStockAppend.prototype.DeleteStockRequest = function(ticker) {
    var self = this;

    node.API.SendCustomCommand(NodeUUID, "db_delete_stock", {
        'ticker': ticker
    }, function(res) {
        var payload = res.data.payload;
        self.ModalDelete.Remove();
        market.DeleteStock(ticker);
        self.GetDataBaseStocks();
    });
}

ModuleStockAppend.prototype.DeleteStock = function(ticker) {
    var self = this;

    var footer = `
        <button type="button" class="btn btn-danger" onclick="window.StockAppend.DeleteStockRequest('[TICKER]');">Yes</button>
        <button type="button" class="btn btn-secondary" data-dismiss="modal" onclick="window.StockAppend.CleanModal();">No</button>
    `;
    
    footer = footer.split("[TICKER]").join(ticker);
    this.ModalDelete.Remove();
    this.ModalDelete.SetTitle("Delete Stock");
    this.ModalDelete.SetContent("Shouls I delete "+ticker+" stock?");
    this.ModalDelete.SetFooter(footer);
    this.ModalDelete.Build("cm");
    this.ModalDelete.Show();
}

ModuleStockAppend.prototype.FindStockInMarket = function() {
    var ticker = document.getElementById('d_m_stock_append_stock_find_ticker').value;
    document.getElementById('id_m_stock_append_info_container').innerHTML = "";

    this.StockGraph = new ModuleStockHistoryGraph("stock_market", ticker);
    this.StockGraph.SetHostingID("d_m_stock_append_stock_graph");
    this.StockGraph.SetObjectDOMName(this.DOMName+".StockGraph");
    this.StockGraph.Build(null, null);

    document.getElementById('id_m_stock_append_add_new_stock').classList.add("d-none");
    // document.getElementById('id_m_stock_append_stock_stocks_view').classList.add("d-none");
    var info = new ModuleStockInfo();
    info.SetHostingID("id_m_stock_append_info_container");
    info.Build(null, function(module) {
        module.GetStockInfo(ticker, function(module) {
            document.getElementById('id_m_stock_append_add_new_stock').classList.remove("d-none");
            // document.getElementById('id_m_stock_append_stock_stocks_view').classList.remove("d-none");
        });
    });
}

ModuleStockAppend.prototype.OpenPortfolioSelectorModal = function(ticker) {
    this.Selector = new ModulePortfolioSelectorView(ticker);
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

ModuleStockAppend.prototype.UpdateStockInfoView = function(ticker) {
    document.getElementById('d_m_stock_append_stock_find_ticker').value = ticker;
    this.FindStockInMarket();
}

ModuleStockAppend.prototype.SimplePredictionUpdate = function(stock) {
    var simpleActionObj = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_simple_action");

    switch (stock.predictions.basic_action) {
        case "sell":
            simpleActionObj.innerHTML = `<span style="color: red;" data-feather="log-out" data-placement="top" data-toggle="tooltip" title="Sell"></span>`;
            break;
        case "buy":
            simpleActionObj.innerHTML = `<span style="color: green;" data-feather="log-in" data-placement="top" data-toggle="tooltip" title="Buy"></span>`;
            break;
        case "hold":
            simpleActionObj.innerHTML = `<span style="color: orange;" data-feather="shield" data-placement="top" data-toggle="tooltip" title="Hold"></span>`;
            break;
        default:
            break;
    }
}

ModuleStockAppend.prototype.UpdateStockTableFromLocalMarket = function() {
    console.log("UpdateStockTableFromLocalMarket");

    this.Earnings   = 0.0;
    this.Number     = 0;

    for (key in market.Stocks) {
        var stock = market.Stocks[key];
        
        var priceEventObj   = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_price_event");
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_market_price").innerHTML = stock.market_price;
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_number").innerHTML = stock.number;
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_earnings").innerHTML = stock.earnings;
        this.Earnings   += stock.earnings;
        this.Number     += stock.number;

        this.SimplePredictionUpdate(stock);
        if (this.CheckThreshold(stock) == true) {
            priceEventObj.innerHTML = `<span style="color: red;" data-feather="alert-triangle" data-placement="top" data-toggle="tooltip" title="Stock At Risk"><span></span>`;
        } else {
            priceEventObj.innerHTML = "";
        }
    }

    document.getElementById("id_m_stock_append_table_price_summery_number").innerHTML   = this.Number;
    document.getElementById("id_m_stock_append_table_price_summery_earnings").innerHTML = this.Earnings.toFixed(2);
    feather.replace();
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
}

ModuleStockAppend.prototype.CheckThreshold = function(stock) {
    var threshold_activated = false;

    if (stock.thresholds.length > 0) {
        for (key in stock.thresholds) {
            threshold = stock.thresholds[key];
            threshold_activated = threshold.activated;
        }
    }

    return threshold_activated;
}

ModuleStockAppend.prototype.UpdateStockTableAsync = function(data, scope) {
    for (key in data) {
        var stock = data[key];
        
        var priceObj        = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_market_price");
        var amountObj       = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_number");
        var earningsObj     = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_earnings");
        var priceEventObj   = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_price_event");

        if (priceObj === undefined || priceObj === null) {
            return;
        }
        
        scope.SimplePredictionUpdate(stock);
        if (scope.CheckThreshold(stock) == true) {
            priceEventObj.innerHTML = `<span style="color: red;" data-feather="alert-triangle" data-placement="top" data-toggle="tooltip" title="Stock At Risk"><span></span>`;
        } else {
            priceEventObj.innerHTML = "";
        }
        
        scope.Number     -= parseFloat(amountObj.innerHTML);
        scope.Earnings   -= parseFloat(earningsObj.innerHTML);
        scope.Number     += stock.number;
        scope.Earnings   += stock.earnings;

        priceObj.innerHTML      = stock.market_price;
        amountObj.innerHTML     = stock.number;
        earningsObj.innerHTML   = stock.earnings;

        document.getElementById("id_m_stock_append_table_price_summery_number").innerHTML   = scope.Number;
        document.getElementById("id_m_stock_append_table_price_summery_earnings").innerHTML = scope.Earnings.toFixed(2);
    }

    feather.replace();
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
}

ModuleStockAppend.prototype.GetDataBaseStocks = function() {
    var self = this;
    
    node.API.SendCustomCommand(NodeUUID, "get_db_stocks", {
    }, function(res) {
        var payload = res.data.payload;
        var table = new MksBasicTable();
        table.SetSchema(["", "", "", "", "", "", ""]);
        var data = [];
        for (key in payload.stocks) {
            stock = payload.stocks[key];
            
            row = [];
            row.push(`<h6 class="my-0"><a href="#" onclick="`+self.DOMName+`.UpdateStockInfoView('`+stock.ticker+`');">`+stock.ticker+`</a></h6>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_market_price">`+stock.market_price+`<span>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_number">0<span>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_earnings">0<span>`);
            row.push(`<div id="id_m_stock_append_table_price_`+stock.ticker+`_simple_action"></div>`);
            row.push(`<div id="id_m_stock_append_table_price_`+stock.ticker+`_price_event"></div>`);
            row.push(`
                <div class="d-flex flex-row-reverse">
                    <div class="dropdown">
                        <button class="btn btn-outline-secondary dropdown-toggle btn-sm" type="button" id="id_m_stock_append_stock_dropdown_`+stock.ticker+`" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <span data-feather="menu"></span>
                        </button>
                        <div class="dropdown-menu text-center" aria-labelledby="id_m_stock_append_stock_dropdown_`+stock.ticker+`">
                            <span class="dropdown-item" style="color: RED; cursor:pointer; font-size: 12px;" onclick="`+self.DOMName+`.OpenActionAppendModal('`+stock.ticker+`','BUY');">Buy</span>
                            <span class="dropdown-item" style="color: GREEN; cursor:pointer; font-size: 12px;" onclick="`+self.DOMName+`.OpenActionAppendModal('`+stock.ticker+`','SELL');">Sell</span>
                            <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+self.DOMName+`.OpenStockActionsHistoryModal('`+stock.ticker+`');">History</span>
                            <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+self.DOMName+`.OpenPortfolioSelectorModal('`+stock.ticker+`');">Portfolios</span>
                            <span class="dropdown-item" style="color: RED; cursor:pointer; font-size: 12px;" onclick="`+self.DOMName+`.DeleteStock('`+stock.ticker+`');">Delete</span>
                        </div>
                    </div>
                </div>
            `);

            data.push(row);
        }
        table.ShowRowNumber(false);
        table.ShowHeader(false);
        table.SetData(data);
        table.AppendSummary([`<h6 style="color: BLUE">Overall</h6>`, "", `<span id="id_m_stock_append_table_price_summery_number" style="color: BLUE">0<span>`, `<span id="id_m_stock_append_table_price_summery_earnings" style="color: BLUE">0<span>`, "", "", ""])
        table.Build(document.getElementById("id_m_stock_append_stock_table"));

        document.getElementById('d_m_stock_append_stock_find_ticker').addEventListener('keyup', function(event) {
            if (event.code === 'Enter') {
                event.preventDefault();
                self.FindStockInMarket(document.getElementById('d_m_stock_append_stock_find_ticker').value);
            }
        });
        // document.getElementById('id_m_stock_append_stock_stocks_view').classList.remove("d-none");
        feather.replace();
        self.UpdateStockTableFromLocalMarket();
    });
}

ModuleStockAppend.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockAppend.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}