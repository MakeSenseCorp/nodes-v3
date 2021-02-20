function ModuleAction() {
    var self = this;

    // Modules basic
    this.HTML 	                    = "";
    this.ActionHTML                 = `
        <div class="container" id="id_m_action_[ID]">
            <div class="py-5 text-center">
                <p class="lead">[ACTION] [TICKER] stocks.</p>
            </div>
            <div class="row">
                <div class="col-lg-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="row">
                                <div class="col">
                                    <input type="number" min="0" data-bind="value:replyNumber" class="form-control" id="id_m_append_action_price" placeholder="Price">
                                </div>
                                <div class="col">
                                    <input type="number" min="0" data-bind="value:replyNumber" class="form-control" id="id_m_append_action_amount" placeholder="Amount">
                                </div>
                                <div class="col">
                                    <input type="number" min="0" data-bind="value:replyNumber" class="form-control" id="id_m_append_action_fee" placeholder="Fee">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    this.HostingID                  = "";
    this.DOMName                    = "";
    // Objects section
    this.ComponentObject            = null;

    return this;
}

ModuleAction.prototype.SetObjectDOMName = function(name) {
    this.DOMName = name;
}

ModuleAction.prototype.SetHostingID = function(id) {
    this.HostingID = id;
}

ModuleAction.prototype.Build = function(data, callback) {
    var self = this;

    var html = this.ActionHTML.replace("[ID]", self.HostingID);
    html = html.split("[ACTION]").join(data.action);
	html = html.split("[TICKER]").join(data.ticker);
    this.HTML = html;
    if (callback !== undefined && callback != null) {
        callback(this);
    }
}

ModuleAction.prototype.AppendStockAction = function(ticker, action, callback) {
    var self = this;
    node.API.SendCustomCommand(NodeUUID, "append_new_action", {
        "ticker": ticker,
        "price": document.getElementById("id_m_append_action_price").value,
        "action": action,
        "amount": document.getElementById("id_m_append_action_amount").value,
        "fee": (document.getElementById("id_m_append_action_fee").value == "") ? "0.0" : document.getElementById("id_m_append_action_fee").value
    }, function(res) {
        var payload = res.data.payload;
        window.Modal.Hide();
        window.Modal.Remove();
    });
}

ModuleAction.prototype.Hide = function() {
    var self = this;
    this.ComponentObject.classList.add("d-none")
}

ModuleAction.prototype.Show = function() {
    var self = this;
    this.ComponentObject.classList.remove("d-none")
}