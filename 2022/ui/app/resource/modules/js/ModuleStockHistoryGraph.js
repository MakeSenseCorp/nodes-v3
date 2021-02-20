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
                            <div class="btn-group" role="group" aria-label="Basic example">
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraph('1d','1m');">1D</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraph('5d','5m');">5D</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraph('1mo','30m');">1MO</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraph('3mo','60m');">3MO</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraph('6mo','1d');">6MO</button>
                                <button type="button" class="btn btn-outline-secondary" onclick="[INSTANCE].UpdateGraph('1y','1d');">1Y</button>
                            </div>
                            <div class="btn-group" role="group" aria-label="Basic example">
                                <button type="button" class="btn btn-outline-secondary">High</button>
                                <button type="button" class="btn btn-outline-secondary">Low</button>
                                <button type="button" class="btn btn-outline-secondary">Regression</button>
                            </div>
                        </div>
                    </div>
                    <hr class="mb-4">
                    <div class="row">
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

    return this;
}

ModuleStockHistoryGraph.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockHistoryGraph.prototype.SetHostingID = function(id) {
    this.HostingID = id;
    this.ID = this.HostingID+"_"+this.Name;
    this.GraphHistoryCtx = new MksBasicGraph("id_m_stock_graph_"+this.ID+"_history");
}

ModuleStockHistoryGraph.prototype.Build = function(data, callback) {
    var html = this.HTML;
    html = html.split("[ID]").join(this.HostingID);
    html = html.split("[NAME]").join(this.Name);
    html = html.split("[TICKER]").join(this.Ticker);
    html = html.split("[INSTANCE]").join(this.DOMName);
    this.ComponentObject = document.getElementById("id_m_stock_graph_"+this.ID);
    document.getElementById(this.HostingID).innerHTML = html;
    this.UpdateGraph('5d','5m');
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

ModuleStockHistoryGraph.prototype.UpdateGraph = function(period, interval) {
    var self = this;
    this.DownloadStockHistory(this.Ticker, period, interval, function(data) {
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
            "color": self.GraphHistoryCtx.Colors.red,
            "bk_color": self.GraphHistoryCtx.Colors.red,
            "title": "Open"
        });
        self.GraphHistoryCtx.AddDataSet({
            "x": data.data.date,
            "y": data.data.regression,
            "color": self.GraphHistoryCtx.Colors.blue,
            "bk_color": self.GraphHistoryCtx.Colors.blue,
            "title": "Regression"
        });
        self.GraphHistoryCtx.Build(document.getElementById("id_m_stock_history_graph_"+self.HostingID+"_"+self.Name));
        /*
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
        self.GraphHistogramCtx.Build(document.getElementById("id_m_stock_histogram_graph_"+self.HostingID+"_"+self.Name));
        */
    });
}

ModuleStockHistoryGraph.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockHistoryGraph.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}
