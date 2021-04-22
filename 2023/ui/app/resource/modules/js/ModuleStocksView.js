function ModuleStocksView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;
    this.Stocks                     = null;
    this.Filter                     = {
        "id_m_funder_stocks_view_us_stocks_checkbox": true,
        "id_m_funder_stocks_view_is_stocks_checkbox": true,
        "id_m_funder_stocks_view_government_stocks_checkbox": true
    }

    return this;
}

ModuleStocksView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStocksView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStocksView.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleStocksView.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);
        self.ComponentObject = document.getElementById("id_m_funder_stocks_view_"+this.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;

        document.getElementById("id_m_funder_stocks_view_us_stocks_checkbox").checked = true;
        document.getElementById("id_m_funder_stocks_view_is_stocks_checkbox").checked = true;
        document.getElementById("id_m_funder_stocks_view_government_stocks_checkbox").checked = true;

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleStocksView.prototype.Clean = function() {
    clearInterval(this.GetStocksTimerHndl);
}

ModuleStocksView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStocksView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}

ModuleStocksView.prototype.FilterOutput = function(obj) {
    this.Filter[obj.id] = obj.checked;
    console.log(this.Stocks);
    var table = new MksBasicTable();
    table.SetSchema(["", "", "", "", ""]);
    var data = [];
    for (key in this.Stocks) {
        rate = this.Stocks[key];

        var show = false;
        if (rate.type == 1001 && this.Filter["id_m_funder_stocks_view_us_stocks_checkbox"] == true) {
            show = true;
        } else if (rate.type == 1 && this.Filter["id_m_funder_stocks_view_is_stocks_checkbox"] == true) {
            show = true;
        } else if (rate.type != 1 && rate.type != 1001 && this.Filter["id_m_funder_stocks_view_government_stocks_checkbox"] == true) {
            show = true;
        } else {
            show = false;
        }

        if (show == true) {
            row = [];
            row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer">`+rate.ticker+`</a></h6>`);
            row.push(`<span>`+rate.name+`</span>`);
            row.push(`<span>`+rate.type+`</span>`);
            row.push(`<span>`+rate.funds_count+`</span>`);
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
    }
    table.ShowRowNumber(false);
    table.ShowHeader(false);
    table.SetData(data);
    table.Build(document.getElementById("id_m_funder_stocks_view_rates_table"));
    feather.replace();
}

ModuleStocksView.prototype.GetStocksRate = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_stocks_rate", {
    }, function(res) {
        var payload = res.data.payload;
        console.log(payload);

        var table = new MksBasicTable();
        table.SetSchema(["", "", "", "", ""]);
        var data = [];
        for (key in payload.ratings) {
            rate = payload.ratings[key];           
            row = [];
            row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer">`+rate.ticker+`</a></h6>`);
            row.push(`<span>`+rate.name+`</span>`);
            row.push(`<span>`+rate.type+`</span>`);
            row.push(`<span>`+rate.funds_count+`</span>`);
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
        table.Build(document.getElementById("id_m_funder_stocks_view_rates_table"));
        feather.replace();
        self.Stocks = Array.from(payload.ratings);
    });
}