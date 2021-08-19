function MksBasicModal (name) {
	self = this;
	this.Name = name;
	
	this.BasicModalContainer = `
		<div class="modal fade bd-example-modal-[SIZE]" id="id_basic_modal_[NAME]" tabindex="-1" role="dialog" aria-labelledby="id_m_basic_modal_[NAME]_label" aria-hidden="true">
			<div class="modal-dialog modal-[SIZE]" role="document">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title" id="id_m_basic_modal_[NAME]_label">[TITLE]</h5>
						<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
						</button>
					</div>
					<div id="id_basic_modal_[NAME]_content" class="modal-body">[CONTENT]</div>
					<div id="id_basic_modal_[NAME]_footer" class="modal-footer">[FOOTER]</div>
				</div>
			</div>
		</div>
	`;
	this.BasicTitle = "Baisc Modal";
	this.BasicModalContent = `
	`;
	this.BasicModalFooter = `
		<h6 class="d-flex justify-content-between align-items-center mb-3">
			<span class="text-muted"><a href="#" onclick="$('#id_basic_modal_[NAME]').modal('hide');">Close</a></span>
		</h6>
	`;
	
	return this;
}

MksBasicModal.prototype.Build = function (modal_size) {
	var obj = document.getElementById("id_basic_modal_"+this.Name);
	if (obj !== undefined && obj !== null) {
		return;
	}
	
	// Update modal UI objects
	var html = this.BasicModalContainer;
	html = html.split("[SIZE]").join(modal_size);
	html = html.split("[CONTENT]").join(this.BasicModalContent);
	html = html.split("[FOOTER]").join(this.BasicModalFooter);
	html = html.split("[TITLE]").join(this.BasicTitle);
	html = html.split("[NAME]").join(this.Name);
	// Create modal in DOM
	var elem = document.createElement('div');
	elem.innerHTML = html;
	document.body.appendChild(elem);	
}

MksBasicModal.prototype.Remove = function () {
	var obj = document.getElementById("id_basic_modal_"+this.Name);
	if (obj !== null) {
		this.Hide();
		obj.parentNode.removeChild(obj);
	}
}

MksBasicModal.prototype.SetTitle = function (title) {
	this.BasicTitle = title;
}

MksBasicModal.prototype.SetContent = function (html) {
	this.BasicModalContent = html;
}

MksBasicModal.prototype.SetFooter = function (html) {
	this.BasicModalFooter = html;
}

MksBasicModal.prototype.UpdateFooter = function (html) {
	this.BasicModalFooter = html;
	document.getElementById("id_basic_modal_"+this.Name+"_content").innerHTML = this.BasicModalFooter;
}

MksBasicModal.prototype.SetDefaultFooter = function () {
	this.BasicModalFooter = `
		<h6 class="d-flex justify-content-between align-items-center mb-3">
			<span class="text-muted"><a href="#" onclick="$('#id_basic_modal_[NAME]').modal('hide');">Close</a></span>
		</h6>
	`;

	var html = this.BasicModalFooter;
	html = html.split("[NAME]").join(this.Name);
	var obj = document.getElementById("id_basic_modal_"+this.Name+"_footer");
	if (obj !== null) {
		obj.innerHTML = html;
	}
}

MksBasicModal.prototype.Show = function () {
	$('#id_basic_modal_'+this.Name).modal('show');
}

MksBasicModal.prototype.Hide = function () {
	$('#id_basic_modal_'+this.Name).modal('hide');
}

