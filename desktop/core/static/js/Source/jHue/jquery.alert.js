/*
* jHue alert plugin
*/
var jHueAlert = function(message){

		if ($("#jHueAlertDialog").length==0){
			var mainDialog = $("<div>").attr("id", "jHueAlertDialog").addClass("modal").addClass("hide").addClass("fade");
			mainDialog.html('<div class="modal-header"><a href="#" class="close">&times;</a></div><div class="modal-body"></div>');
			mainDialog.appendTo("body");
			mainDialog.modal({
				backdrop: "static",
				keyboard: true
			});
		}
		var alertDialog= $("#jHueAlertDialog");
		alertDialog.find(".modal-body").text(message);
		alertDialog.modal("show");
};
