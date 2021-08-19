function MksBlockTable () {
	self = this;

    this.WorkingObject  = null;
    this.Head           = "";
    this.Body           = "";
    this.Row            = `
        <li class="list-group-item d-flex justify-content-between lh-condensed">
            <div>
                <h6 class="my-0">[ITEM_#1]</h6>
                <small class="text-muted">[ITEM_#2]</small>
            </div>
            <span class="text-muted">[ITEM_#3]</span>
        </li>
    `;
    this.Content        = `
        <ul class="list-group mb-3">
            [BODY]
        </ul>
    `;
	
	return this;
}

MksBlockTable.prototype.SetData = function (data) {
	this.Body = "";
    for (idx = 0; idx < data.length; idx++) {
        html = this.Row;
        html = html.split("[ITEM_#1]").join(data[idx].item1);
        html = html.split("[ITEM_#2]").join(data[idx].item2);
        html = html.split("[ITEM_#3]").join(data[idx].item3);
        this.Body += html;
    }
}

MksBlockTable.prototype.Build = function (obj) {
    this.WorkingObject = obj;
    var html = this.Content;
	
    html = html.split("[HEAD]").join(this.Head);
    html = html.split("[BODY]").join(this.Body);
    obj.innerHTML = html;
}

MksBlockTable.prototype.Remove = function () {
	if (this.WorkingObject !== undefined && this.WorkingObject !== null) {
		this.WorkingObject.parentNode.removeChild(this.WorkingObject);
	}
}