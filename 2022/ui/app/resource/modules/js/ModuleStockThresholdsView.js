function ModuleStockThresholdsView(ticker) {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.HostingID                  = "";
    this.DOMName                    = "";
    this.MainView                   = `
                                        <form>
                                            <div class="form-group row">
                                                <div class="col-sm-12">
                                                    <div class="custom-control custom-checkbox">
                                                        <input type="checkbox" class="custom-control-input" onclick="[DOM].SetAutomatedThreshold(this);" id="id_m_stock_threshold_automated">
                                                        <label class="custom-control-label" for="id_m_stock_threshold_automated">Automated threshold</label>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group row">
                                                <div class="col-sm-4">
                                                    <div class="custom-control custom-checkbox">
                                                        <input type="checkbox" class="custom-control-input" onclick="[DOM].EnableThreshold(this, 10);" id="id_m_stock_threshold_enable_upper">
                                                        <label class="custom-control-label" for="id_m_stock_threshold_enable_upper">Enable</label>
                                                    </div>
                                                </div>
                                                <div class="col-sm-4">
                                                    <label for="id_m_stock_threshold_upper_threshold" class="col-sm-8 col-form-label">Upper</label>
                                                </div>
                                                <div class="col-sm-4">
                                                    <input type="text" class="form-control" id="id_m_stock_threshold_upper_threshold" value="0">
                                                </div>
                                            </div>
                                            <div class="form-group row">
                                                <div class="col-sm-4">
                                                    <div class="custom-control custom-checkbox">
                                                        <input type="checkbox" class="custom-control-input" onclick="[DOM].EnableThreshold(this, 11);" id="id_m_stock_threshold_enable_lower">
                                                        <label class="custom-control-label" for="id_m_stock_threshold_enable_lower">Enable</label>
                                                    </div>
                                                </div>
                                                <div class="col-sm-4">
                                                    <label for="id_m_stock_threshold_lower_threshold" class="col-sm-8 col-form-label">Lower</label>
                                                </div>
                                                <div class="col-sm-4">
                                                    <input type="text" class="form-control" id="id_m_stock_threshold_lower_threshold" value="0">
                                                </div>
                                            </div>
                                        </form>
                                    `;
    // Objects section
    this.HostingObject              = null;
    this.ComponentObject            = null;
    this.Ticker                     = ticker;
    this.Upper                      = {
        "id": 0,
        "value": 0.0,
        "enabled": false
    };
    this.Lower                      = {
        "id": 0,
        "value": 0.0,
        "enabled": false
    };

    return this;
}

ModuleStockThresholdsView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleStockThresholdsView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleStockThresholdsView.prototype.EnableThreshold = function(obj, type) {
    switch (type) {
        case 10:
            this.Upper.enabled = obj.checked;
            break;
        case 11:
            this.Lower.enabled = obj.checked;
            break;
        default:
            break;
    }
}

ModuleStockThresholdsView.prototype.UpdateStockThresholds = function(callback) {
    var self = this;
    var upperValue = document.getElementById("id_m_stock_threshold_upper_threshold").value;
    var lowerValue = document.getElementById("id_m_stock_threshold_lower_threshold").value;
    node.API.SendCustomCommand(NodeUUID, "threshold", {
        "ticker": this.Ticker,
        "action": "update",
        "upper": {
            "id": this.Upper.id,
            "value": upperValue,
            "enabled": this.Upper.enabled
        },
        "lower": {
            "id": this.Lower.id,
            "value": lowerValue,
            "enabled": this.Lower.enabled
        }
    }, function(res) {
        var payload = res.data.payload;
        if (callback !== undefined && callback != null) {
            callback();
        }
    });
}

ModuleStockThresholdsView.prototype.GetStockThresholds = function() {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "threshold", {
        "ticker": this.Ticker,
        "action": "select"
    }, function(res) {
        var payload = res.data.payload;
        var thresholds = payload.thresholds;
        if (thresholds !== undefined && thresholds !== null) {
            if (thresholds.length > 0) {
                for (key in thresholds) {
                    var threshold = thresholds[key];
                    if (threshold.type == 10) {
                        self.Upper.id = threshold.id;
                        self.Upper.value = threshold.value;
                        self.Upper.enabled = (threshold.enabled == 1) ? true: false;
                        document.getElementById("id_m_stock_threshold_enable_upper").checked = (threshold.enabled == 1) ? true: false;
                        document.getElementById("id_m_stock_threshold_upper_threshold").value = threshold.value;
                    } else if (threshold.type == 11) {
                        self.Lower.id = threshold.id;
                        self.Lower.value = threshold.value;
                        self.Lower.enabled = (threshold.enabled == 1) ? true: false;
                        document.getElementById("id_m_stock_threshold_enable_lower").checked = (threshold.enabled == 1) ? true: false;
                        document.getElementById("id_m_stock_threshold_lower_threshold").value = threshold.value;
                    }
                }
            }
        }
    });
}

ModuleStockThresholdsView.prototype.Build = function(data, callback) {
    var self = this;
    
    self.HTML = self.MainView;
    self.HTML = self.HTML.split("[DOM]").join(self.DOMName);

    self.HostingObject = document.getElementById(self.HostingID);
    if (self.HostingObject !== undefined && self.HostingObject != null) {
        self.HostingObject.innerHTML = self.HTML;
    }

    if (callback !== undefined && callback != null) {
        callback(self);
    }
}

ModuleStockThresholdsView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleStockThresholdsView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}