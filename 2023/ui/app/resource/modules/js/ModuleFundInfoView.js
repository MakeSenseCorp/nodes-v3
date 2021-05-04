function ModuleFundInfoView(number) {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    this.Number                     = number;
    // Objects section
    this.ComponentObject            = null;

    return this;
}

ModuleFundInfoView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleFundInfoView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleFundInfoView.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleFundInfoView.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);

        if (self.HostingID != "") {
            self.ComponentObject = document.getElementById("id_m_funder_info_view_"+self.HostingID);
            document.getElementById(self.HostingID).innerHTML = self.HTML;
        }

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleFundInfoView.prototype.TableUIChangeEvent = function() {
    feather.replace();
}

ModuleFundInfoView.prototype.GetAllFundInfo = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "get_fund_info", {
        "number": this.Number
    }, function(res) {
        var payload = res.data.payload;
        console.log(payload);

        var table = new MksBasicTable();
        table.SetSchema(["", "", "", "", ""]);
        table.EnableListing();
        table.SetListingWindowSize(10);
        table.RegisterUIChangeEvent(self.TableUIChangeEvent);
        var data = [];
        for (key in payload.holdings) {
            holding = payload.holdings[key];           
            row = [];
            row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer" onclick="">`+holding.ticker+`</a></h6>`);
            row.push(`<span>`+holding.val+`</span>`);
            row.push(`<span>`+holding.amount+`</span>`);
            row.push(`<span>`+holding.perc+`</span>`);
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
        table.Build(document.getElementById("id_m_funder_fun_info_view_holdings_table"));
        feather.replace();
    });
}

ModuleFundInfoView.prototype.Clean = function() {
    clearInterval(this.GetStocksTimerHndl);
}

ModuleFundInfoView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleFundInfoView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}