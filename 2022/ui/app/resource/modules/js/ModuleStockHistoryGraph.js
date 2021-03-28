function ModuleStockHistoryGraph(name, ticker) {
    var self = this;

    // Modules basic
    this.HTML 	                = `
    <div class="row" id="id_m_stock_graph_[ID]_[NAME]">
        <div class="col-lg-12">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-lg-12 text-center">
                            <div id="id_m_stock_graph_period_selector_[ID]_[NAME]" class="btn-group btn-group-sm" role="group" aria-label="Basic example">
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraphUI(this,'1d','1m');">1D</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraphUI(this,'5d','5m');">5D</button>
                                <button type="button" class="btn btn-outline-secondary active" onclick="[INSTANCE].UpdateGraphUI(this,'1mo','30m');">1MO</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraphUI(this,'3mo','60m');">3MO</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraphUI(this,'6mo','1d');">6MO</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraphUI(this,'1y','1d');">1Y</button>
                            </div>
                        </div>
                    </div>
                    <hr class="mb-4">
                    <div class="row">
                        <div class="col-xl-12 d-none" style="text-align: center;" id="id_m_stock_history_loader_[ID]_[NAME]">
                            <br>
                            <div class="spinner-border text-primary" role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                            <br>
                            <br>
                        </div>
                        <div class="col-lg-12">
                            <div id="id_m_stock_history_graph_[ID]_[NAME]"></div>
                            <br/>
                            <div id="id_m_stock_histograme_graph_[ID]_[NAME]"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
    this.ID                     = "";
    this.HostingID              = "";
    this.Name                   = name;
    this.DOMName                = "";
    this.Ticker                 = ticker;
    // Objects section
    this.ComponentObject        = null;
    this.GraphHistoryCtx 	    = null;
    this.GraphHistogramCtx 	    = null;

    return this;
}

ModuleStockHistoryGraph.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockHistoryGraph.prototype.SetHostingID = function(id) {
    this.HostingID = id;
    this.ID = this.HostingID+"_"+this.Name;
    this.GraphHistoryCtx = new MksBasicGraph("id_m_stock_graph_"+this.ID+"_history");
    this.GraphHistogramCtx = new MksBasicGraph("id_m_stock_graph_"+this.ID+"_histograme");
}

ModuleStockHistoryGraph.prototype.Build = function(data, callback) {
    var html = this.HTML;
    html = html.split("[ID]").join(this.HostingID);
    html = html.split("[NAME]").join(this.Name);
    html = html.split("[TICKER]").join(this.Ticker);
    html = html.split("[INSTANCE]").join(this.DOMName);
    this.ComponentObject = document.getElementById("id_m_stock_graph_"+this.ID);
    document.getElementById(this.HostingID).innerHTML = html;
    this.UpdateGraph('1mo','30m');
    if (callback !== undefined && callback != null) {
        callback(this);
    }
}

ModuleStockHistoryGraph.prototype.DownloadStockHistory = function(ticker, period, interval, callback) {
    node.API.SendCustomCommand(NodeUUID, "download_stock_history", {
        "ticker": ticker,
        "period": period,
        "interval": interval
    }, function(res) {
        var payload = res.data.payload;
        callback(payload);
    });
}

ModuleStockHistoryGraph.prototype.UpdateGraphUI = function(obj, period, interval) {
    var selector = document.getElementById("id_m_stock_graph_period_selector_"+this.ID);
    var kids = selector.children;
    for (var i = 0; i < kids.length; i++) {
        kids[i].classList.remove("active");
    }
    obj.classList.add("active");
    this.UpdateGraph(period, interval);
}

ModuleStockHistoryGraph.prototype.UpdateGraph = function(period, interval) {
    var self = this;
    this.ShowLoader();
    this.DownloadStockHistory(this.Ticker, period, interval, function(data) {
        if (data.data == null || data.data === undefined) {
            return;
        }

        pmin = [];
        pmax = [];
        for (idx = 0; idx < data.data.date.length; idx++) {
            pmin.push(data.data.min);
            pmax.push(data.data.max);
        }

        self.GraphHistoryCtx.Configure({
            "type": "line",
            "title": "Stock Price",
            "x": {
                "title": "Days"
            },
            "y": {
                "title": "Price"
            }
        });
        self.GraphHistoryCtx.CleanConfigure();
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": data.data.open,
            "color": 'rgb(100, 100, 100)',
            "bk_color": 'rgb(100, 100, 100)',
            "title": "Open"
        });
        /*
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": data.data.regression,
            "color": self.GraphHistoryCtx.Colors.yellow,
            "bk_color": self.GraphHistoryCtx.Colors.yellow,
            "title": "Regression"
        });
        */
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": data.data.algo.perc_low,
            "color": self.GraphHistoryCtx.Colors.red,
            "bk_color": self.GraphHistoryCtx.Colors.red,
            "title": "Buy",
            "dashed": true
        });
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": data.data.algo.perc_high,
            "color": self.GraphHistoryCtx.Colors.green,
            "bk_color": self.GraphHistoryCtx.Colors.green,
            "title": "Sell",
            "dashed": true
        });
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": data.data.algo.perc_mid,
            "color": self.GraphHistoryCtx.Colors.orange,
            "bk_color": self.GraphHistoryCtx.Colors.orange,
            "title": "Middle",
            "dashed": true
        });
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": pmin,
            "color": self.GraphHistoryCtx.Colors.grey,
            "bk_color": self.GraphHistoryCtx.Colors.grey,
            "title": "Min",
            "dashed": true
        });
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": pmax,
            "color": self.GraphHistoryCtx.Colors.grey,
            "bk_color": self.GraphHistoryCtx.Colors.grey,
            "title": "Max",
            "dashed": true
        });
        self.GraphHistoryCtx.Build(document.getElementById("id_m_stock_history_graph_"+self.HostingID+"_"+self.Name));
        self.HideGraphLoader();
        
        self.GraphHistogramCtx.Configure({
            "type": "bar",
            "title": "Price Histograme",
            "x": {
                "title": "Count"
            },
            "y": {
                "title": "Price"
            }
        });
        self.GraphHistogramCtx.CleanConfigure();
        self.GraphHistogramCtx.AddDataSet({
            "x": data.data.hist_open.x,
            "y": data.data.hist_open.y,
            "color": self.GraphHistogramCtx.Colors.orange,
            "bk_color": self.GraphHistogramCtx.Colors.blue,
            "title": "Price Histograme"
        });
        
        self.GraphHistogramCtx.Build(document.getElementById("id_m_stock_histograme_graph_"+self.HostingID+"_"+self.Name));
    });
}

ModuleStockHistoryGraph.prototype.HideGraphLoader = function() {
    var self = this;
    document.getElementById("id_m_stock_history_loader_"+self.HostingID+"_"+self.Name).classList.add("d-none");
}

ModuleStockHistoryGraph.prototype.ShowLoader = function() {
    var self = this;
    document.getElementById("id_m_stock_history_loader_"+self.HostingID+"_"+self.Name).classList.remove("d-none");
}

ModuleStockHistoryGraph.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none");
}

ModuleStockHistoryGraph.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none");
}
