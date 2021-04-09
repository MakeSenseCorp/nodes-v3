function ModuleStockInfo() {
    var self = this;

    // Modules basic
    this.HTML 	                = "";
    this.HostingID              = "";
    // Objects section
    this.ComponentObject        = null;
    this.CompanyNameObject 		= null;
    this.CompanyCountryObject 	= null;
    this.CompanySectorObject 	= null;
    this.CompanyIndustryObject 	= null;

    return this;
}

ModuleStockInfo.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStockInfo.prototype.Build = function(data, callback) {
    var self = this;

    node.API.GetFileContent(NodeUUID, {
        "file_path": "modules/html/ModuleStockInfo.html"
    }, function(res) {
        var payload = res.data.payload;
        self.HTML = MkSGlobal.ConvertHEXtoString(payload.content).replace("ModuleStockInfo", "id_m_stock_info_"+self.HostingID);
        document.getElementById(self.HostingID).innerHTML = self.HTML;
        self.CompanyNameObject      = document.getElementById("id_m_stock_info_stock_company_name");
        self.CompanyCountryObject   = document.getElementById("id_m_stock_info_stock_company_country");
        self.CompanySectorObject    = document.getElementById("id_m_info_stock_stock_company_sector");
        self.CompanyIndustryObject  = document.getElementById("id_m_info_stock_stock_company_industry");
        self.Price                  = document.getElementById("id_m_stock_info_stock_price");
        self.Volume                 = document.getElementById("id_m_stock_info_stock_volume");
        self.Divident               = document.getElementById("id_m_stock_info_stock_divident");
        self.Beta                   = document.getElementById("id_m_info_stock_stock_beta");
        self.FloatShares            = document.getElementById("id_m_stock_info_stock_float_shares");
        self.ComponentObject        = document.getElementById("id_m_stock_info_"+self.HostingID);
        self.PercentileAmplitudeObj = document.getElementById("id_m_stock_info_stock_percentile_amplitude");
        self.Hide();
        callback(self);
    });
}

ModuleStockInfo.prototype.GetDataFromObject = function(data) {
    if (data == null || data === undefined) {
        return "";
    }

    if (typeof(data) === "object") {
        return data.fmt;
    }
    return data;
}

ModuleStockInfo.prototype.GetStockInfo = function(ticker, callback) {
    if (ticker === undefined || ticker === null) {
        return false;
    }

    this.ShowLoader();
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "download_stock_info", {
        "ticker": ticker
    }, function(res) {
        var payload = res.data.payload;
        self.CompanyNameObject.innerHTML 		= self.GetDataFromObject(payload.info.shortName);
        self.CompanyCountryObject.innerHTML 	= self.GetDataFromObject(payload.info.country);
        self.CompanySectorObject.innerHTML 	    = self.GetDataFromObject(payload.info.sector);
        self.CompanyIndustryObject.innerHTML 	= self.GetDataFromObject(payload.info.industry);
        // self.Price.innerHTML                    = self.GetDataFromObject(payload.info.previousClose); // payload.info.ask;
        self.Price.innerHTML                    = self.GetDataFromObject(payload.info.price); // payload.info.ask;
        self.Volume.innerHTML                   = self.GetDataFromObject(payload.info.volume);
        self.Divident.innerHTML                 = self.GetDataFromObject(payload.info.dividendRate);
        self.Beta.innerHTML                     = self.GetDataFromObject(payload.info.beta);
        self.FloatShares.innerHTML              = self.GetDataFromObject(payload.info.floatShares);
        self.Show();
        self.HideLoader();
        callback(self);
    });
}

ModuleStockInfo.prototype.UpdatePercentileAnplitudeValue = function(value) {
    this.PercentileAmplitudeObj.innerHTML = value.toFixed(2);
}

ModuleStockInfo.prototype.HideLoader = function() {
    document.getElementById("id_m_stock_info_stock_loader").classList.add("d-none");
}

ModuleStockInfo.prototype.ShowLoader = function() {
    document.getElementById("id_m_stock_info_stock_loader").classList.remove("d-none");
}

ModuleStockInfo.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockInfo.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}