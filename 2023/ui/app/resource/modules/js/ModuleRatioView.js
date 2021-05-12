function ModuleRatioView() {
    var self = this;

    // Modules basic
    this.HTML 	                    = `
        <div class="row justify-content-xl-center">
            <div class="col-xl-12">
                <h5 class="mb-3">Search filter</h5>
                <hr>
                <div class="row justify-content-xl-center">
                    <div class="col-xl-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="row justify-content-xl-center">
                                    <div class="col-xl-4">
                                        <div class="form-check form-check-inline">
                                            <input class="form-check-input" type="checkbox" id="id_m_funder_dashboard_view_funds_table_filter_us_fund_fee_check" value="option1">
                                            <label class="form-check-label" for="id_m_funder_dashboard_view_funds_table_filter_us_fund_fee_check">
                                                <strong><span>Fee</span></strong>
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-xl-8">
                                        <div id="id_m_funder_dashboard_view_funds_slider_fee"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <br>
                <div class="row justify-content-xl-center">
                    <div class="col-xl-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="row justify-content-xl-center">
                                    <div class="col-xl-4">
                                        <div class="form-check form-check-inline">
                                            <input class="form-check-input" type="checkbox" id="id_m_funder_dashboard_view_funds_table_filter_us_stock_perc_check" value="option1">
                                            <label class="form-check-label" for="id_m_funder_dashboard_view_funds_table_filter_us_stock_perc_check">
                                                <strong><span>US %</span></strong>
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-xl-8">
                                        <div id="id_m_funder_dashboard_view_funds_slider_us_perc"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <br>
                <div class="row justify-content-xl-center">
                    <div class="col-xl-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="row justify-content-xl-center">
                                    <div class="col-xl-4">
                                        <div class="form-check form-check-inline">
                                            <input class="form-check-input" type="checkbox" id="id_m_funder_dashboard_view_funds_table_filter_is_stock_perc_check" value="option1">
                                            <label class="form-check-label" for="id_m_funder_dashboard_view_funds_table_filter_is_stock_perc_check">
                                                <strong><span>IS %</span></strong>
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-xl-8">
                                        <div id="id_m_funder_dashboard_view_funds_slider_is_perc"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <br>
                <div class="row justify-content-xl-center">
                    <div class="col-xl-12">
                        <div class="card">
                            <div class="card-body">
                                <div class="row justify-content-xl-center">
                                    <div class="col-xl-4">
                                        <div class="form-check form-check-inline">
                                            <input class="form-check-input" type="checkbox" id="id_m_funder_dashboard_view_funds_table_filter_other_stock_perc_check" value="option1">
                                            <label class="form-check-label" for="id_m_funder_dashboard_view_funds_table_filter_other_stock_perc_check">
                                                <strong><span>Other %</span></strong>
                                            </label>
                                        </div>
                                    </div>
                                    <div class="col-xl-8">
                                        <div id="id_m_funder_dashboard_view_funds_slider_other_perc"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    this.ID                         = "";
    this.HostingID                  = "";
    this.GraphModule                = null;
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;

    this.FeeSlider = new MksMultiRangeSlider({
        min: 0,
        max: 5,
        step: 0.1,
        left: 0,
        right: 5
    });
    this.USPercentSlider = new MksMultiRangeSlider({
        min: 0,
        max: 100,
        step: 1,
        left: 0,
        right: 100
    });
    this.ISPercentSlider = new MksMultiRangeSlider({
        min: 0,
        max: 100,
        step: 1,
        left: 0,
        right: 100
    });
    this.OtherPercentSlider = new MksMultiRangeSlider({
        min: 0,
        max: 100,
        step: 1,
        left: 0,
        right: 100
    });
    this.FeeEnabled     = false;
    this.UsEnabled      = false;
    this.IsEnabled      = false;
    this.OtherEnabled   = false;

    this.FeeCheckbox    = null;
    this.UsCheckbox     = null;
    this.IsCheckbox     = null;
    this.OtherCheckbox  = null;

    return this;
}

ModuleRatioView.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleRatioView.prototype.SetHostingID = function(id) {
    this.HostingID = id;
    this.ID = this.HostingID+"_"+this.Name;
}

ModuleRatioView.prototype.Build = function(data, callback) {
    var self = this;

    if (this.HostingID != "") {
        document.getElementById(this.HostingID).innerHTML = this.HTML;
    }

    if (callback !== undefined && callback != null) {
        callback(this);
    }
}

ModuleRatioView.prototype.CheckBoxUpdate = function() {
    if (this.FeeCheckbox === undefined || this.FeeCheckbox === null) {
        this.FeeEnabled = false;
    } else {
        if (this.FeeCheckbox.checked == true) {
            this.FeeEnabled = true;
        } else {
            this.FeeEnabled = false;
        }
    }

    if (this.UsCheckbox === undefined || this.UsCheckbox === null) {
        this.UsEnabled = false;
    } else {
        if (this.UsCheckbox.checked == true) {
            this.UsEnabled = true;
        } else {
            this.UsEnabled = false;
        }
    }

    if (this.IsCheckbox === undefined || this.IsCheckbox === null) {
        this.IsEnabled = false;
    } else {
        if (this.IsCheckbox.checked == true) {
            this.IsEnabled = true;
        } else {
            this.IsEnabled = false;
        }
    }

    if (this.OtherCheckbox === undefined || this.OtherCheckbox === null) {
        this.OtherEnabled = false;
    } else {
        if (this.OtherCheckbox.checked == true) {
            this.OtherEnabled = true;
        } else {
            this.OtherEnabled = false;
        }
    }
}

ModuleRatioView.prototype.GenrateComponents = function(conf) {
    this.FeeSlider = new MksMultiRangeSlider({
        min: 0,
        max: 5,
        step: 0.1,
        left: conf.fee.left,
        right: conf.fee.right
    });
    this.FeeSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_fee"));
    this.USPercentSlider = new MksMultiRangeSlider({
        min: 0,
        max: 100,
        step: 1,
        left: conf.us.left,
        right: conf.us.right
    });
    this.USPercentSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_us_perc"));
    this.ISPercentSlider = new MksMultiRangeSlider({
        min: 0,
        max: 100,
        step: 1,
        left: conf.is.left,
        right: conf.is.right
    });
    this.ISPercentSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_is_perc"));
    this.OtherPercentSlider = new MksMultiRangeSlider({
        min: 0,
        max: 100,
        step: 1,
        left: conf.other.left,
        right: conf.other.right
    });
    this.OtherPercentSlider.Build(document.getElementById("id_m_funder_dashboard_view_funds_slider_other_perc"));

    this.FeeCheckbox = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_fund_fee_check");
    if (conf.fee.enabled == true) {
        this.FeeCheckbox.checked = true;
    }
    this.UsCheckbox = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_us_stock_perc_check");
    if (conf.us.enabled == true) {
        this.UsCheckbox.checked = true;
    }
    this.IsCheckbox = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_is_stock_perc_check");
    if (conf.is.enabled == true) {
        this.IsCheckbox.checked = true;
    }
    this.OtherCheckbox  = document.getElementById("id_m_funder_dashboard_view_funds_table_filter_other_stock_perc_check");
    if (conf.other.enabled == true) {
        this.OtherCheckbox.checked = true;
    }
}

ModuleRatioView.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleRatioView.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}