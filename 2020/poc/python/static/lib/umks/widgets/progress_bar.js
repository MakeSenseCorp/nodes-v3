function MksBasicProgressBar (name) {
	self 					= this;
	this.API 				= null;
    this.Name               = name
    this.PrecentageView     = true;
	this.OnUploadCompete 	= null;
	
	this.BasicContainer = `
        <div id="id-progress-object-[NAME]">
            <div class="progress">
                <div id="id-progress-bar-[NAME]" class="progress-bar progress-bar-striped" style="min-width: 20px;"></div>
            </div>
            <div>
                <span class="text-muted" id="id-progress-item-[NAME]">0%</span>
            </div>
        </div>
	`;
	
	return this;
}

MksBasicProgressBar.prototype.EnableInnerPercentageText = function (status) {
	this.PrecentageView = status;
}

MksBasicProgressBar.prototype.Build = function (obj) {
	var html = this.BasicContainer;
	html = html.split("[NAME]").join(this.Name);
    obj.innerHTML = html;
}

MksBasicProgressBar.prototype.UpdateProgress = function (data) {
    var innerPrecentageMessage = ""
    if (this.PrecentageView == true) {
        innerPrecentageMessage = data.precentage+"%";
    }
    $("#id-progress-bar-"+this.Name).css("width", data.precentage+"%").text(innerPrecentageMessage);
	
	document.getElementById("id-progress-item-"+this.Name).innerHTML = data.message;
	switch(data.status) {
		case "inprogress":
			break;
		case "error":
			break;
		case "done":
			if (this.OnUploadCompete !== null) {
				this.OnUploadCompete(data.file);
			}
			break;
	}
}

MksBasicProgressBar.prototype.SetMessage = function (message) {
    document.getElementById("id-progress-item-"+this.Name).innerHTML = message;
}

MksBasicProgressBar.prototype.Show = function () {
    document.getElementById("id-progress-object-"+this.Name).classList.remove("d-none");
}

MksBasicProgressBar.prototype.Hide = function () {
    document.getElementById("id-progress-object-"+this.Name).classList.add("d-none");
}