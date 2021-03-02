var G_MODULE_IMPORT_ACTIONS_IMPORT_DATA = [];
function ModuleImportActions() {
    var self = this;

    // Modules basic
    this.HTML 	                            = "";
    this.HostingID                          = "";
    this.DOMName                            = "";
    this.ImportDataCreatePortfolioChecked   = false;
    this.ImportData                         = [];
    this.Uploader                           = null;
    // Objects section
    this.ComponentObject                    = null;

    return this;
}

ModuleImportActions.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleImportActions.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleImportActions.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleImportActions.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("[ID]", self.HostingID);

        self.HostingObject = document.getElementById(self.HostingID);
        if (self.HostingObject !== undefined && self.HostingObject != null) {
            // this.ComponentObject = document.getElementById("id_m_portfolio_"+this.HostingID);
            self.HostingObject.innerHTML = self.HTML;
        }

        if (callback !== undefined && callback != null) {
            callback(self);
        }
    });
}

ModuleImportActions.prototype.BuildUploader = function() {
    var objUploader = document.getElementById("id-basic-uploader-installer");
    this.Uploader = MksBasicUploaderBuilder.GetInstance();
    this.Uploader.SetAPI(node.API);
    this.Uploader.SetFileType(["ms-excel","csv"])
    this.Uploader.OnUploadCompete = this.OnUploadCompleteHandler;
    // Build DOM UI for Uploader
    this.Uploader.Build(objUploader, "Upload");
}

ModuleImportActions.prototype.ImportStocksCreateNewPortfolio = function(obj) {
    this.ImportDataCreatePortfolioChecked = obj.checked;
    if (obj.checked == true) {
        document.getElementById("id_m_ipmort_stocks_portfolio_name_block").classList.remove("d-none");
    } else {
        document.getElementById("id_m_ipmort_stocks_portfolio_name_block").classList.add("d-none");
    }
}

ModuleImportActions.prototype.ImportStocks = function(id) {
    var self = this;
				
    if (this.ImportDataCreatePortfolioChecked == true && document.getElementById("id_m_ipmort_stocks_portfolio_name").value == "") {
        alert("Portfolio name is empty");
        return;
    }
    
    node.API.SendCustomCommand(NodeUUID, "import_stocks", {
        "stocks": G_MODULE_IMPORT_ACTIONS_IMPORT_DATA,
        "portfolio_checked": this.ImportDataCreatePortfolioChecked,
        "portfolio_name": document.getElementById("id_m_ipmort_stocks_portfolio_name").value
    }, function(res) {
        var payload = res.data.payload;
        window.Modal.Hide();
        window.Modal.Remove();
        self.ImportData = [];
    });
}

ModuleImportActions.prototype.OnUploadCompleteHandler = function(file) {
    var self = this;
    // Load CSV file and send stocks information.
    node.API.SendCustomCommand(NodeUUID, "load_csv", {
        "file_name": file
    }, function(res) {
        var payload = res.data.payload;
        var table = new MksBasicTable();
        table.SetSchema(["", "Date", "Ticker", "Price", "Amount", "Fee", "Action", "Exist"]);
        var data = [];
        var importData = [];
        for (key in payload.stocks) {
            stock = payload.stocks[key];
            row = [];
            row.push(stock.date);
            row.push(stock.ticker);
            row.push(stock.price);
            row.push(stock.amount);
            row.push(stock.fee);
            if (stock.action == "Buy") {
                row.push("<strong><span style='color:RED'>BUY</span></strong>");
            } else {
                row.push("<strong><span style='color:GREEN'>SELL</span></strong>");
            }
            if (stock.exists == 1) {
                row.push("");
            } else {
                row.push("<strong><span style='color:GREEN'>New Stock</span></strong>");
            }
            
            data.push(row);

            action = (stock.action.toLowerCase() == "buy") ? -1 : 1;
            fee = stock.fee.replace("$","")
            fee = (fee == "") ? "0.0" : fee;
            importData.push({
                'date': stock.date,
                'ticker': stock.ticker,
                'price': stock.price.replace("$",""),
                'amount': stock.amount,
                'fee': fee,
                'action': action
            })
        }
        table.SetData(data);
        table.Build(document.getElementById("id_import_stocks_table"));
        console.log(">",importData);
        G_MODULE_IMPORT_ACTIONS_IMPORT_DATA = Array.from(importData);
        document.getElementById("id_m_ipmort_stocks_block").classList.remove("d-none");
    });
}

ModuleImportActions.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleImportActions.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}