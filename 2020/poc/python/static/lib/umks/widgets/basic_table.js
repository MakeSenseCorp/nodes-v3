function MksBasicTable () {
	self = this;

    this.WorkingObject  = null;
    this.Head           = "";
    this.Body           = "";
    this.Content        = `
        <div class="table-responsive">
            <table class="table table-sm [STRIPED] table-hover">
                <thead>
                    <tr>
                        [HEAD]
                    </tr>
                </thead>
                <tbody>
                    [BODY]
                </tbody>
            </table>
        </div>
    `;
	this.Striped    = false;
    this.RowsNumber = false;
    this.HeaderShow = true;
	
	return this;
}

MksBasicTable.prototype.SetStriped = function () {
	this.Striped = true;
}

MksBasicTable.prototype.ShowRowNumber = function (value) {
	this.RowsNumber = value;
}

MksBasicTable.prototype.ShowHeader = function (value) {
	this.HeaderShow = value;
}

MksBasicTable.prototype.SetSchema = function (schema) {
    this.Head = "";
    for (idx = 0; idx < schema.length; idx++) {
        this.Head += "<th scope='col'>" + schema[idx] + "</th>";
    }
}

MksBasicTable.prototype.SetData = function (data) {
	this.Body = "";
    for (idx = 0; idx < data.length; idx++) {
        if (this.RowsNumber == true) {
            this.Body += "<tr><th scope='row'>"+(idx+1)+"</th>";
        } else {
            this.Body += "<tr>";
        }
        
        for (ydx = 0; ydx < data[idx].length; ydx++) {
            this.Body += "<td>" + data[idx][ydx] + "</td>";
        }
        this.Body += "</tr>";
    }
}

MksBasicTable.prototype.AppendSummary = function (data) {
    this.Body += "<tr class='table-dark'>";
    for (idx = 0; idx < data.length; idx++) {
        this.Body += "<td>"+data[idx]+"</td>";
    } this.Body += "</tr>";
}

MksBasicTable.prototype.Build = function (obj) {
    this.WorkingObject = obj;
    var html = this.Content;
	
	if (this.Striped == true) {
		html = html.split("[STRIPED]").join("table-striped");
	} else {
		html = html.split("[STRIPED]").join('');
	}
	
    if (this.HeaderShow == true) {
        html = html.split("[HEAD]").join(this.Head);
    } else {
        html = html.split("[HEAD]").join("");
    }
    
    html = html.split("[BODY]").join(this.Body);
    obj.innerHTML = html;
}

MksBasicTable.prototype.Remove = function () {
    if (this.WorkingObject !== undefined && this.WorkingObject !== null) {
		this.WorkingObject.parentNode.removeChild(this.WorkingObject);
	}
}