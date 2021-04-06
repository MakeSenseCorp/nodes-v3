function ModuleDashboardView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;

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
        self.ComponentObject = document.getElementById("id_m_stocks_view_"+this.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;

        nasdaq.UpcommingEvents(function(events) {
            console.log(events);            
            for (key in events) {
                var event = events[key];
                if (event.name == "IPOs") {
                    var data = [];
                    var table = new MksBasicTable();
                    table.SetSchema(["", ""]);
                    for (idx in event.iposList) {
                        var ipo = event.iposList[idx];
                        console.log(ipo);
                        row = [];
                        row.push(`<h8 class="my-0"><a href="#" onclick="">`+ipo.companyName+`</a></h8>`);
                        row.push(`<div>`+ipo.price+`</div>`);
                        data.push(row);
                    }
                    table.ShowRowNumber(false);
                    table.ShowHeader(false);
                    table.SetData(data);
                    table.Build(document.getElementById("id_m_dashboard_view_next_ipos"));
                }

                if (event.name == "Dividends") {
                    var data = [];
                    var table = new MksBasicTable();
                    table.SetSchema(["", ""]);
                    for (idx in event.dividendsList) {
                        var divident = event.dividendsList[idx];
                        console.log(ipo);
                        row = [];
                        row.push(`<h8 class="my-0"><a href="#" onclick="">`+divident.companyName+`</a></h8>`);
                        row.push(`<div>`+divident.exDivDate+`</div>`);
                        data.push(row);
                    }
                    table.ShowRowNumber(false);
                    table.ShowHeader(false);
                    table.SetData(data);
                    table.Build(document.getElementById("id_m_dashboard_view_next_dividents"));
                }
            }
        });

        nasdaq.RecentArticles(function(articles) {
            var table = new MksBasicTable();
            table.SetSchema(["", ""]);
            var data = [];
            for (key in articles) {
                aticle = articles[key];
                row = [];
                row.push(`<h8 class="my-0"><a href="#" onclick="">`+aticle.title+`</a></h8>`);
                row.push(`<div>`+aticle.ago+`</div>`);
                data.push(row);
            }
            table.ShowRowNumber(false);
            table.ShowHeader(false);
            table.SetData(data);
            table.Build(document.getElementById("id_m_dashboard_view_recent_articales"));
        });

        if (callback !== undefined && callback != null) {
            callback(self);
        }
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