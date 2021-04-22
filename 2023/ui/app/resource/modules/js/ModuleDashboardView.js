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

    return this;
}

ModuleDashboardView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleDashboardView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
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
    console.log(number);
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
    node.API.SendCustomCommand(NodeUUID, "get_all_funds", {
    }, function(res) {
        var payload = res.data.payload;
        console.log(payload);

        var table = new MksBasicTable();
        table.SetSchema(["", "", "", "", "", "", "", "", "", "", "", "", ""]);
        var data = [];
        for (key in payload.funds) {
            fund = payload.funds[key];           
            row = [];
            row.push(`<h6 class="my-0"><a style="color:blue; cursor:pointer" onclick="window.DashboardView.OpenFundInfoModal(`+fund.number+`)">`+fund.number+`</a></h6>`);
            row.push(`<span>`+fund.name+`</span>`);
            row.push(`<span>`+fund.mngr+`</span>`);
            row.push(`<span>`+fund.ivest_mngr+`</span>`);
            row.push(`<span>`+fund.d_change+`</span>`);
            row.push(`<span>`+fund.month_begin+`</span>`);
            row.push(`<span>`+fund.y_change+`</span>`);
            row.push(`<span>`+fund.year_begin+`</span>`);
            row.push(`<span>`+fund.fee+`</span>`);
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