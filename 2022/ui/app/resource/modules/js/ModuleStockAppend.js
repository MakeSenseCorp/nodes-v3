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
    this.StockInfo                  = null;
    this.Selector                   = null;
    this.PortfolioList              = null;
    this.StockLoaderProgressBar	    = null;
    this.Thresholds                 = null;
    // Portfolio
    this.PortfolioID 	            = 0;
    this.PortfolioName              = "All";
    this.Earnings                   = 0.0;
    this.Number                     = 0;
    this.TotalInvestment            = 0.0;
    this.TotalStockDiff             = 0.0;
    this.TotalCurrentInvestment     = 0.0;
    this.ModalDelete                = new MksBasicModal("m_stock_append_delete");
    this.BasicPredictionViewType    = -1;
    this.BasicPredictionViewName    = "1MO";

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

    console.log("ModuleStockAppend.Build");
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

ModuleStockAppend.prototype.IsStockInPortfolio = function(stock, id) {
    if (id == 0) {
        return true;
    }

    for (key in stock.portfolios) {
        if (stock.portfolios[key] == id) {
            return true;
        }
    }

    return false;
}

ModuleStockAppend.prototype.UpdateUI = function(scope, stocks) {
    scope.Earnings               = 0.0;
    scope.Number                 = 0;
    scope.TotalInvestment        = 0.0;
    scope.TotalCurrentInvestment = 0.0;
    
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", "", "", "", "", ""]);
    var data = [];
    for (key in stocks) {
        stock = stocks[key];
        if (scope.IsStockInPortfolio(stock, scope.PortfolioID)) {
            scope.Earnings               += stock.earnings;
            scope.Number                 += stock.number;
            scope.TotalInvestment        += stock.total_investment;
            scope.TotalCurrentInvestment += stock.number * stock.market_price;
            
            row = [];
            row.push(`<h6 class="my-0"><a href="#" onclick="`+scope.DOMName+`.UpdateStockInfoView('`+stock.ticker+`');">`+stock.ticker+`</a></h6>`);
            row.push(`<div id="id_m_stock_append_table_price_`+stock.ticker+`_simple_action"></div>`);
            row.push(`<div id="id_m_stock_append_table_price_`+stock.ticker+`_price_event"></div>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_market_price">`+stock.market_price+`</span>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_market_price_diff"></span>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_number">`+stock.number+`<span>`);
            row.push(`<span id="id_m_stock_append_table_price_`+stock.ticker+`_earnings">`+stock.earnings+`<span>`);
            row.push(`
                <div class="d-flex flex-row-reverse">
                    <div class="dropdown">
                        <button class="btn btn-outline-secondary dropdown-toggle btn-sm" type="button" id="id_m_stock_append_stock_dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <span data-feather="menu"></span>
                        </button>
                        <div class="dropdown-menu text-center" aria-labelledby="id_m_stock_append_stock_dropdown">
                            <span class="dropdown-item" style="color: RED; cursor:pointer; font-size: 12px;" onclick="`+scope.DOMName+`.OpenActionAppendModal('`+stock.ticker+`','BUY');">Buy</span>
                            <span class="dropdown-item" style="color: GREEN; cursor:pointer; font-size: 12px;" onclick="`+scope.DOMName+`.OpenActionAppendModal('`+stock.ticker+`','SELL');">Sell</span>
                            <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+scope.DOMName+`.OpenStockActionsHistoryModal('`+stock.ticker+`');">History</span>
                            <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+scope.DOMName+`.OpenPortfolioSelectorModal('`+stock.ticker+`');">Portfolios</span>
                            <span class="dropdown-item" style="color: BLUE; cursor:pointer; font-size: 12px;" onclick="`+scope.DOMName+`.OpenThresholdModal('`+stock.ticker+`');">Thresholds</span>
                            <span class="dropdown-item" style="color: RED; cursor:pointer; font-size: 12px;" onclick="`+scope.DOMName+`.DeleteStock('`+stock.ticker+`');">Delete</span>
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
    table.AppendSummary([`<h6 style="color: BLUE">Overall</h6>`, "", "", `<span id="id_m_stock_append_table_price_summary_total_nvestment" style="color: BLUE">0<span>`, `<span id="id_m_stock_append_table_price_summary_total_stock_diff" style="color: BLUE">0<span>`, `<span id="id_m_stock_append_table_price_summery_number" style="color: BLUE">0<span>`, `<span id="id_m_stock_append_table_price_summery_earnings" style="color: BLUE">0<span>`, ""])
    table.Build(document.getElementById("id_m_stock_append_stock_table"));
    scope.UpdateStockTableFromLocalMarket();
    feather.replace();
}

ModuleStockAppend.prototype.UpdateTableSammaryUI = function(data) {
    if (data !== undefined && data !== null) {
        var objForCheck = document.getElementById("id_m_stock_append_table_price_summary_total_stock_diff");
        if (objForCheck !== undefined && objForCheck !== null) {
            document.getElementById("id_m_stock_append_table_price_summary_total_stock_diff").innerHTML = data.total_stock_diff.toFixed(2);
            document.getElementById("id_m_stock_append_table_price_summery_number").innerHTML           = data.stocks_count;
            document.getElementById("id_m_stock_append_table_price_summery_earnings").innerHTML         = data.earnings.toFixed(2);
            document.getElementById("id_m_stock_append_table_price_summary_total_nvestment").innerHTML  = data.total_current_investment.toFixed(2); // `${data.total_current_investment.toFixed(2)} (${data.total_investment.toFixed(2)}) $`;
        }
    }
}

ModuleStockAppend.prototype.GetPortfolioStocks = function(id, name) {
    var self = this;
    this.PortfolioID = id;
    // Update table stock ui
    this.UpdateUI(this, market.Stocks);
    // Update sammary table stock ui
    market.GetPortfolioStatistics(this.PortfolioID, function(data) {
        self.UpdateTableSammaryUI(data);
    });
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

ModuleStockAppend.prototype.StockGraphDataChangeHandler = function(ticker) {
    window.StockAppend.StockInfo.UpdatePercentileAnplitudeValue(window.StockAppend.StockGraph.PercentileHigh - window.StockAppend.StockGraph.PercentileLow);
    window.StockAppend.StockInfo.UpdateSTDValue(window.StockAppend.StockGraph.Statistics.std);
}

ModuleStockAppend.prototype.FindStockInMarket = function() {
    var self = this;
    var ticker = document.getElementById('d_m_stock_append_stock_find_ticker').value;
    document.getElementById('id_m_stock_append_info_container').innerHTML = "";

    this.StockGraph = new ModuleStockHistoryGraph("stock_market", ticker);
    this.StockGraph.SetGraphViewType(this.BasicPredictionViewName);
    this.StockGraph.SetHostingID("d_m_stock_append_stock_graph");
    this.StockGraph.SetObjectDOMName(this.DOMName+".StockGraph");
    this.StockGraph.SetDataChangeCallback(this.StockGraphDataChangeHandler);
    this.StockGraph.Build(null, null);

    document.getElementById('id_m_stock_append_info_basic_prediction').classList.add("d-none");
    document.getElementById('id_m_stock_append_add_new_stock').classList.add("d-none");
    this.StockInfo = new ModuleStockInfo();
    this.StockInfo.SetHostingID("id_m_stock_append_info_container");
    this.StockInfo.Build(null, function(module) {
        module.GetStockInfo(ticker, function(module) {
            var stock = market.GetStockFromCache(ticker);
            if (stock !== undefined && stock !== null) {
                var html  = self.GenerateSimplePredictionHtml(stock.predictions.basic);
                document.getElementById('id_m_stock_append_info_basic_prediction').innerHTML = html;
                feather.replace();
                document.getElementById('id_m_stock_append_info_basic_prediction').classList.remove("d-none");
            } else {
                // Show append buton
                document.getElementById('id_m_stock_append_add_new_stock').classList.remove("d-none");
                node.API.SendCustomCommand(NodeUUID, "calulate_basic_prediction", {
                    "ticker": ticker
                }, function(res) {
                    var payload = res.data.payload;
                    var stock = payload.stock;
                    var html  = self.GenerateSimplePredictionHtml(stock.predictions.basic);
                    document.getElementById('id_m_stock_append_info_basic_prediction').innerHTML = html;
                    feather.replace();
                    document.getElementById('id_m_stock_append_info_basic_prediction').classList.remove("d-none");
                });
            }
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

ModuleStockAppend.prototype.SaveThresholds = function() {
    this.Thresholds.UpdateStockThresholds(function() {
        console.log("SaveThresholds... Done..");
        window.Modal.Hide();
    });
}

ModuleStockAppend.prototype.OpenThresholdModal = function(ticker) {
    var self = this;
    this.Thresholds = new ModuleStockThresholdsView(ticker);
    this.Thresholds.SetObjectDOMName(this.DOMName+".Thresholds");
    this.Thresholds.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Thresholds");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.SetFooter(`<button type="button" id="modal_optimize_run" class="btn btn-success" onclick="window.StockAppend.SaveThresholds();">Save</button><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("sm");
        window.Modal.Show();
        self.Thresholds.GetStockThresholds(ticker);
    });
}

ModuleStockAppend.prototype.OpenBasicPredictionModal = function(ticker) {
    var stock = market.GetStockFromCache(ticker);
    var html  = this.GenerateSimplePredictionHtml(stock.predictions.basic);
    
    window.Modal.Remove();
    window.Modal.SetTitle("Basic Prediction");
    window.Modal.SetContent(html);
    window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
    window.Modal.Build("lg");
    window.Modal.Show();
    feather.replace();
}

ModuleStockAppend.prototype.UpdateStockInfoView = function(ticker) {
    document.getElementById('d_m_stock_append_stock_find_ticker').value = ticker;
    this.FindStockInMarket();
}

ModuleStockAppend.prototype.CheckThreshold = function(stock, like) {
    var threshold_activated = false;

    if (stock.thresholds.length > 0) {
        for (key in stock.thresholds) {
            threshold = stock.thresholds[key];
            if (threshold.name.includes(like)) {
                threshold_activated = threshold.activated;
            }
        }
    }

    return threshold_activated;
}

ModuleStockAppend.prototype.CalculateTotalSimplePrediction = function(prediction) {
    var prediction_map = {
        "sell": -1,
        "hold": 0,
        "buy": 1
    }

    var prediction_weight = {
        0: 1,
        1: 2,
        2: 3,
        3: 2,
        4: 1,
        5: 1
    }

    var hold = 0;
    var buy  = 0;
    var sell = 0;

    var prediction_overall = 0;
    // Calculate overall basic prediction [1D(0), 5D(1), 1MO(2), 3MO(3), 6MO(4)]
    for (key in prediction) {
        var pred = prediction[key].action.current;
        if (pred == "hold") {
            hold += prediction_weight[key];
        } else if (pred == "sell") {
            sell += 0 - prediction_weight[key];
        } else {
            buy += prediction_weight[key];
        }
    }

    prediction_overall = sell + buy;
    if (prediction_overall < 0 && hold > 0 - prediction_overall) {
        prediction_overall = 0;
    } else if (prediction_overall > 0 && hold > prediction_overall) {
        prediction_overall = 0;
    }

    return prediction_overall;
}

ModuleStockAppend.prototype.GenerateSimplePredictionHtml = function(prediction) {
    var html = `<div class="card"><div class="card-body">
                <div class="row">
                    <div class="col text-center"><span>1D</span></div>
                    <div class="col text-center"><span>5D</span></div>
                    <div class="col text-center"><span>1MO</span></div>
                    <div class="col text-center"><span>3MO</span></div>
                    <div class="col text-center"><span>6MO</span></div>
                    <div class="col text-center"><span>1Y</span></div>
                    <div class="col text-center"><span></span></div>
                    <div class="col text-center"><span>Total</span></div>
                </div>
                <div class="row">`;
    var prediction_map = {
        "sell": -1,
        "hold": 0,
        "buy": 1
    }

    var prediction_weight = {
        0: 1,
        1: 2,
        2: 3,
        3: 2,
        4: 1,
        5: 1
    }

    var hold = 0;
    var buy = 0;
    var sell = 0;
    var prediction_overall = 0;

    // Calculate overall basic prediction [1D(0), 5D(1), 1MO(2), 3MO(3), 6MO(4)]
    for (key in prediction) {
        var pred = prediction[key].action.current;
        if (pred == "sell") {
            html += `<div class="col text-center"><span style="color: red; cursor: pointer;" data-feather="log-out" data-placement="top" data-toggle="tooltip" title="Sell"></span></div>`;
        } else if (pred == "buy") {
            html += `<div class="col text-center"><span style="color: green;cursor: pointer;" data-feather="log-in" data-placement="top" data-toggle="tooltip" title="Buy"></span></div>`;
        } else if (pred == "hold") {
            html += `<div class="col text-center"><span style="color: orange;cursor: pointer;" data-feather="shield" data-placement="top" data-toggle="tooltip" title="Hold"></span></div>`;
        } else { }

        if (pred == "hold") {
            hold += prediction_weight[key];
        } else if (pred == "sell") {
            sell += 0 - prediction_weight[key];
        } else {
            buy += prediction_weight[key];
        }
    }

    html += `<div class="col text-center">=</div>`

    prediction_overall = sell + buy;
    console.log(prediction_overall, sell, buy, hold);
    if (prediction_overall < 0 && hold > 0 - prediction_overall) {
        prediction_overall = 0;
    } else if (prediction_overall > 0 && hold > prediction_overall) {
        prediction_overall = 0;
    }

    if (prediction_overall < 0) {
        html += `<div class="col text-center"><span style="color: red; cursor: pointer;" data-feather="log-out" data-placement="top" data-toggle="tooltip" title="Sell"></span></div>`;
    } else if (prediction_overall > 0) {
        html += `<div class="col text-center"><span style="color: green;cursor: pointer;" data-feather="log-in" data-placement="top" data-toggle="tooltip" title="Buy"></span></div>`;
    } else if (prediction_overall == 0) {
        html += `<div class="col text-center"><span style="color: orange;cursor: pointer;" data-feather="shield" data-placement="top" data-toggle="tooltip" title="Hold"></span></div>`;
    } else { }

    html += `</div></div></div>`
    return html;
}

ModuleStockAppend.prototype.SelectPredictionType = function(type, name) {
    this.BasicPredictionViewType = type;
    if (type == -1) {
        this.BasicPredictionViewName = "1MO";
    } else {
        this.BasicPredictionViewName = name;
    }
    this.UpdateStockTableFromLocalMarket();
}

ModuleStockAppend.prototype.SimplePredictionUpdate = function(stock) {
    var simpleActionObj = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_simple_action");

    var prediction_map = {
        "sell": -1,
        "hold": 0,
        "buy": 1
    }

    var pred_value = 0;
    if (this.BasicPredictionViewType == -1) {
        pred_value = this.CalculateTotalSimplePrediction(stock.predictions.basic);
    } else {
        pred_value = prediction_map[stock.predictions.basic[this.BasicPredictionViewType].action.current];
    }

    if (pred_value < 0) {
        simpleActionObj.innerHTML = `<span style="color: red; cursor: pointer;" onclick="window.StockAppend.OpenBasicPredictionModal('`+stock.ticker+`');" data-feather="log-out" data-placement="top" data-toggle="tooltip" title="Sell"></span>`;
    } else if (pred_value > 0) {
        simpleActionObj.innerHTML = `<span style="color: green;cursor: pointer;" onclick="window.StockAppend.OpenBasicPredictionModal('`+stock.ticker+`');" data-feather="log-in" data-placement="top" data-toggle="tooltip" title="Buy"></span>`;
    } else if (pred_value == 0) {
        simpleActionObj.innerHTML = `<span style="color: orange;cursor: pointer;" onclick="window.StockAppend.OpenBasicPredictionModal('`+stock.ticker+`');" data-feather="shield" data-placement="top" data-toggle="tooltip" title="Hold"></span>`;
    } else { }
}

ModuleStockAppend.prototype.UpdateStockTableFromLocalMarket = function() {
    console.log("UpdateStockTableFromLocalMarket");

    this.Earnings               = 0.0;
    this.Number                 = 0;

    for (key in market.Stocks) {
        var stock = market.Stocks[key];

        var priceObj = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_market_price");
        if (priceObj === undefined || priceObj === null) {
            continue;
        }
        
        var stockPriceDiff  = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_market_price_diff");
        var stock_diff = stock.market_price - stock.prev_market_price;
        var priceEventObj   = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_price_event");
        priceObj.innerHTML  = stock.market_price;
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_number").innerHTML = stock.number;
        document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_earnings").innerHTML = stock.earnings;
        stockPriceDiff.innerHTML = stock_diff.toFixed(2);
        this.Earnings               += stock.earnings;
        this.Number                 += stock.number;

        stockPriceDiff.style.color = "green";
        if (stock_diff < 0) {
            stockPriceDiff.style.color = "red";
        }

        this.SimplePredictionUpdate(stock);
        if (this.CheckThreshold(stock, "risk") == true) {
            priceEventObj.innerHTML = `<span style="color: red;" data-feather="alert-triangle" data-placement="top" data-toggle="tooltip" title="Stock At Risk"><span></span>`;
        } else if (this.CheckThreshold(stock, "limit") == true) {
            priceEventObj.innerHTML = `<span style="color: green;" data-feather="alert-triangle" data-placement="top" data-toggle="tooltip" title="Stock At Risk"><span></span>`;
        } else {
            priceEventObj.innerHTML = "";
        }
    }

    feather.replace();
    // $("body").tooltip({ selector: '[data-toggle=tooltip]' });
}

ModuleStockAppend.prototype.UpdateStockTableAsync = function(data, scope) {
    for (key in data) {
        var stock = data[key];
        
        var priceObj        = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_market_price");
        var amountObj       = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_number");
        var earningsObj     = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_earnings");
        var priceEventObj   = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_price_event");
        var stockPriceDiff  = document.getElementById("id_m_stock_append_table_price_"+stock.ticker+"_market_price_diff");

        if (priceObj === undefined || priceObj === null) {
            continue;
        }
        
        scope.SimplePredictionUpdate(stock);
        if (scope.CheckThreshold(stock, "risk") == true) {
            priceEventObj.innerHTML = `<span style="color: red;" data-feather="alert-triangle" data-placement="top" data-toggle="tooltip" title="Stock At Risk"><span></span>`;
        } else if (scope.CheckThreshold(stock, "limit") == true) {
            priceEventObj.innerHTML = `<span style="color: green;" data-feather="alert-triangle" data-placement="top" data-toggle="tooltip" title="Stock At Risk"><span></span>`;
        } else {
            priceEventObj.innerHTML = "";
        }
        
        var price_diff                  = stock.market_price - stock.prev_market_price;

        scope.Number                    -= parseFloat(amountObj.innerHTML);
        scope.Earnings                  -= parseFloat(earningsObj.innerHTML);
        scope.Number                    += stock.number;
        scope.Earnings                  += stock.earnings;

        priceObj.innerHTML          = stock.market_price;
        amountObj.innerHTML         = stock.number;
        earningsObj.innerHTML       = stock.earnings;
        stockPriceDiff.innerHTML    = `${price_diff.toFixed(2)}`;
        stockPriceDiff.style.color = "green";
        if (price_diff < 0) {
            stockPriceDiff.style.color = "red";
        }
    }

    feather.replace();
    market.GetPortfolioStatistics(scope.PortfolioID, function(data) {
        scope.UpdateTableSammaryUI(data);
    });
}

ModuleStockAppend.prototype.GetDataBaseStocks = function() {
    var self = this;
    
    node.API.SendCustomCommand(NodeUUID, "get_db_stocks", {
    }, function(res) {
        var payload = res.data.payload;
        self.PortfolioID = 0;
        // Update table stock ui
        self.UpdateUI(self, payload.stocks);
        // Update sammary table stock ui
        market.GetPortfolioStatistics(self.PortfolioID, function(data) {
            self.UpdateTableSammaryUI(data);
        });
    });
}

ModuleStockAppend.prototype.OpenStatisticsModal = function(portfolio_id) {
    var self = this;

    console.log("OpenStatisticsModal");

    window.MKS.Statistics.PortfolioHistoryChange = new ModulePortfolioHistoryChange();
    window.MKS.Statistics.PortfolioHistoryChange.SetHostingID("portfolio_history_change_modal");
    window.MKS.Statistics.PortfolioHistoryChange.SetObjectDOMName("window.MKS.Statistics.PortfolioHistoryChange");
    window.MKS.Statistics.PortfolioHistoryChange.Build(null, function(module) {
        window.Modal.Remove();
        window.Modal.SetTitle("Portfolio History Change");
        window.Modal.SetContent(module.HTML);
        window.Modal.SetFooter(`<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>`);
        window.Modal.Build("lg");
        window.Modal.Show();

        module.SetPotfolioId(0);
        // module.GetStockList();
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