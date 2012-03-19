/*
* jHue selector plugin
* it tranforms a select multiple into a searchable/selectable alphabetical list
*/
;(function ($, window, document, undefined) {

	var pluginName = "jHueSelector",
	defaults = {
		selectAllLabel: "Select all",
		searchPlaceholder: "Search"
	};

	function Plugin(element, options) {
		this.element = element;
		this.options = $.extend({}, defaults, options) ;
		this._defaults = defaults;
		this._name = pluginName;
		this.init();
	}

	Plugin.prototype.setOptions = function(options) {
		this.options = $.extend({}, defaults, options) ;
	};

	Plugin.prototype.init = function () {
		var _this = this;
		var addressBook = [];
		var selectorContainer = $("<div>").addClass("jHueSelector");
		$(_this.element).hide();
		$(_this.element).find("option").each(function(cnt, opt){
			var initial = $(opt).text().substr(0,1).toLowerCase();
			if (addressBook[initial] == null){
				addressBook[initial] = [];
			}
			addressBook[initial].push($(opt));
		});
		var sortedKeys = [];
		for (var key in addressBook){
			sortedKeys.push(key);
		}
		sortedKeys.sort();

		var body = $("<div>").addClass("jHueSelectorBody");
		body.appendTo(selectorContainer);

		for (var i=0; i<sortedKeys.length; i++){
			var key = sortedKeys[i];
			var ul = $("<ul>");
			var dividerLi = $("<li>").addClass("selectorDivider");
			dividerLi.html("<strong>"+key.toUpperCase()+"</strong>");
			dividerLi.appendTo(ul);
			$.each(addressBook[key], function(cnt, opt){
				var li = $("<li>");
				var lbl = $("<label>").text(opt.text());
				var chk = $("<input>").attr("type","checkbox").addClass("selector").change(function(){
					if ($(this).is(":checked")){
						$(this).data("opt").attr("selected", "selected");
					}
					else {
						$(this).data("opt").removeAttr("selected");
					}
				}).data("opt",opt).prependTo(lbl);
                if (opt.is(":selected")){
                    chk.attr("checked","checked");
                }
				lbl.appendTo(li);
				li.appendTo(ul);
			});
			ul.appendTo(body);
		}

		var header = $("<div>").addClass("jHueSelectorHeader");
		header.prependTo(selectorContainer);

		var selectAll = $("<label>").text(this.options.selectAllLabel);
		$("<input>").attr("type","checkbox").change(function(){
			var isChecked = $(this).is(":checked");
			selectorContainer.find("input.selector:visible").each(function(){
				if (isChecked){
					$(this).attr("checked", "checked");
					$(this).data("opt").attr("selected", "selected");
				}
				else {
					$(this).removeAttr("checked");
					$(this).data("opt").removeAttr("selected");
				}
			});
			if (searchBox.val() != ""){
				$(this).removeAttr("checked");
			}
		}).prependTo(selectAll);
		selectAll.appendTo(header);

		var searchBox = $("<input>").attr("type","text").attr("placeholder", this.options.searchPlaceholder).keyup(function(){
			var q = $.trim($(this).val());
			if (q != ""){
				body.find("li.selectorDivider").hide();
				body.find("label").each(function(){
					if ($(this).text().toLowerCase().indexOf(q) > -1){
						$(this).show();
					}
					else {
						$(this).hide();
					}
				});
			}
			else {
				body.find("li.selectorDivider").show();
				body.find("label").show();
			}
		});
		searchBox.prependTo(header);

		$(_this.element).after(selectorContainer);
	};

	$.fn[pluginName] = function (options) {
		return this.each(function () {
			if (!$.data(this, 'plugin_' + pluginName)) {
				$.data(this, 'plugin_' + pluginName, new Plugin( this, options));
			}
			else {
				$.data(this, 'plugin_' + pluginName).setOptions(options);
			}
		});
	}

})(jQuery, window, document);
