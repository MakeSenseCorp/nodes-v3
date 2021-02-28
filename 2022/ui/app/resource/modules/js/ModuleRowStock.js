function ModuleRowStock() {
    var self = this;

    // Modules basic
    this.HTML 	                = "";
    this.HostingID              = "";
    // Objects section
    this.ComponentObject        = null; 
    // Static HTML section
    this.RowHTML = `
        <div class="col-lg-12">
            <div class="alert alert-[BORDER_COLOR]" role="alert">
                <div class="row">
                    <div class="col-lg-9">
                        <div class="row">
                            <div class="col-lg-2">
                                <h5><span style="color: BLUE; cursor:pointer" id="id_m_row_stock_ticker_[TICKER]"></span></h5>
                            </div>
                            <div class="col-lg-1">
                                <h5><span class="badge badge-secondary badge-pill" id="id_m_row_stock_ammount_[TICKER]"></span></h5>
                            </div>
                            <div class="col-lg-2">
                                <h6 id="id_m_row_stock_price_[TICKER]"></h6>
                            </div>
                            <div class="col-lg-2">
                                <span>(</span><span style="font-weight: bold" id="id_m_row_stock_earnings_[TICKER]"></span><span>)</span>
                            </div>
                            <div class="col-lg-2">
                                <span id="id_stock_table_weekly_max_min_slope_[TICKER]"></span>
                            </div>
                            <div class="col-lg-3">
                                <div class="progress" id="id_m_row_stock_stock_line_[TICKER]"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3">
                        <div class="row">
                            <div class="col-lg-3">
                                <button type="button" class="btn btn-sm btn-outline-danger" onclick="ui.OpenModalAction('[TICKER]','BUY');">BUY</button>
                            </div>
                            <div class="col-lg-3">
                                <button type="button" class="btn btn-sm btn-outline-success" onclick="ui.OpenModalAction('[TICKER]','SELL');">SELL</button>
                            </div>
                            <div class="col-lg-6">
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="ui.OpenModalStockDetails('[TICKER]');">Details</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    this.BlockHTML = `
        <div class="col-sm-6 col-lg-4 mb-4 text-center">
            <div class="card mb-4 shadow-sm">
                <div class="card-header">
                    <h4 class="d-flex justify-content-between align-items-center mb-3">
                        <span style="color: BLUE; cursor:pointer" id="id_m_row_stock_ticker_[TICKER]">[TICKER]</span>
                        <small class="badge badge-secondary badge-pill" id="id_m_row_stock_ammount_[TICKER]"></small>
                    </h4>
                </div>
                <div class="card-body">
                    <h3 class="card-title pricing-card-title">
                        <small id="id_m_row_stock_price_[TICKER]"></small>
                        <small>(</small><small style="font-weight: bold" id="id_m_row_stock_earnings_[TICKER]"></small><small>)</small>
                    </h3>
                    <ul class="list-unstyled mt-3 mb-4">
                        <li id="id_stock_table_weekly_max_min_slope_[TICKER]"></li>
                        <li id="id_stock_table_monthly_max_min_slope_[TICKER]"></li>
                        <li>
                            <div class="container mb-4">
                                <hr class="mb-4">
                                <div class="progress" id="id_m_row_stock_stock_line_[TICKER]"></div>
                            </div>
                        </li>
                    </ul>
                    <div class="row">
                        <div class="col">
                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="ui.OpenModalAction('[TICKER]','BUY');">BUY</button>
                        </div>
                        <div class="col">
                            <button type="button" class="btn btn-sm btn-outline-success" onclick="ui.OpenModalAction('[TICKER]','SELL');">SELL</button>
                        </div>
                        <div class="col">
                            <button type="button" class="w-100 btn btn-sm btn-outline-primary" onclick="ui.OpenModalStockDetails('[TICKER]');">Details</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    return this;
}

ModuleRowStock.prototype.Build = function(data, callback=null) {
    var html = "";
    if (data.ui_size === "sm") {
        html = this.RowHTML;
    } else if (data.ui_size === "lg") {
        html = this.BlockHTML;
    } else if (data.ui_size === "xl") {
        return "";
    } else {
        return "";
    }

    html = html.split("[TICKER]").join(data.ticker);

    // border-[BORDER_COLOR]
    
    /*
    var line = new StockLine();
    html = html.split("[STOCK_LINE]").join(line.Build({
        price: data.market_price,
        min: data.hist_price_min,
        max: data.hist_price_max
    }));
    html = html.split("[TICKER]").join(data.ticker);
    html = html.split("[PRICE]").join(data.market_price);
    html = html.split("[EARNINGS]").join(data.earnings);
    html = html.split("[AMMOUNT]").join(data.number);
    html = html.split("[PRICE_COLOR]").join("BLUE");
    // console.log(data.warning);
    if (data.warning == 1) {
        html = html.split("[TICKER_COLOR]").join("ORANGE");
    } else {
        html = html.split("[TICKER_COLOR]").join("");
    }
    if (data.earnings < 0) {
        html = html.split("[EARNINGS_COLOR]").join("RED");
        html = html.split("[BORDER_COLOR]").join("danger");
    } else {
        html = html.split("[EARNINGS_COLOR]").join("GREEN");
        html = html.split("[BORDER_COLOR]").join("success");
    }
    html = html.split("[WEEK_MIN]").join(data.statistics.weekly.min);
    html = html.split("[WEEK_MAX]").join(data.statistics.weekly.max);
    html = html.split("[WEEK_SLOPE]").join(data.statistics.weekly.slope);
    html = html.split("[MONTH_MIN]").join(data.statistics.monthly.min);
    html = html.split("[MONTH_MAX]").join(data.statistics.monthly.max);
    html = html.split("[MONTH_SLOPE]").join(data.statistics.monthly.slope);
    if (data.statistics.weekly.slope < 0) {
        html = html.split("[WEEKLY_SLOPE_COLOR]").join("RED");
    } else {
        html = html.split("[WEEKLY_SLOPE_COLOR]").join("GREEN");
    }
    if (data.statistics.monthly.slope < 0) {
        html = html.split("[MONTHLY_SLOPE_COLOR]").join("RED");
    } else {
        html = html.split("[MONTHLY_SLOPE_COLOR]").join("GREEN");
    }
    */

    return html;
}

ModuleRowStock.prototype.RowExist = function(ticker) {
    var objTicker = document.getElementById("id_m_row_stock_ticker_"+ticker);
    return (objTicker !== undefined && objTicker !== null);
}

ModuleRowStock.prototype.SetTicker = function(ticker) {
    var objTicker = document.getElementById("id_m_row_stock_ticker_"+ticker);
    objTicker.innerHTML = ticker;
}

ModuleRowStock.prototype.SetPrice = function(ticker, price) {
    var objPrice = document.getElementById("id_m_row_stock_price_"+ticker);
    objPrice.innerHTML = price;
}

ModuleRowStock.prototype.SetAmomunt = function(ticker, ammount) {
    var objAmmount = document.getElementById("id_m_row_stock_ammount_"+ticker);
    objAmmount.innerHTML = ammount;
}

ModuleRowStock.prototype.SetEarnings = function(ticker, earnings) {
    var objEarnings = document.getElementById("id_m_row_stock_earnings_"+ticker);
    objEarnings.innerHTML = earnings;

    objEarnings.style.color = "GREEN";
    if (earnings < 0) {
        objEarnings.style.color = "RED";
    }
}

ModuleRowStock.prototype.SetStockLine = function(data) {
    var objStockLine = document.getElementById("id_m_row_stock_stock_line_"+data.ticker);
    var line = new StockLine();
    objStockLine.innerHTML = line.Build({
        price: data.market_price,
        min: data.hist_price_min,
        max: data.hist_price_max
    });
}

ModuleRowStock.prototype.Hide = function() {
    var self = this;
}

ModuleRowStock.prototype.Show = function() {
    var self = this;
}