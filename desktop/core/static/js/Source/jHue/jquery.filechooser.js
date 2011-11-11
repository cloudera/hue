/*
* jHue fileChooser plugin
*/
;(function ($, window, document, undefined) {

	var pluginName = "jHueFileChooser",
	defaults = {
		initialPath: "",
		createFolder: false,
		uploadFile: false,
		onFileChoose: function(){}
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
	
	Plugin.prototype.navigateTo = function (path) {
		var _parent = this;
		$(_parent.element).empty();
		$.getJSON("/filebrowser/chooser"+path, function(data){
			var _flist = $("<ul>");
			$(data.files).each(function(cnt, file){
				var _f = $("<li>");
				var _flink = $("<a>");
				_flink.attr("href","#").text(file.name).appendTo(_f);
				if (file.type == "dir"){
					_flink.click(function(){
						_parent.navigateTo(file.path);
					});
				}
				if (file.type == "file"){
					_flink.click(function(){
						_parent.options.onFileChoose(file.path)
					});
				}
				_f.appendTo(_flist);
			});
			_flist.appendTo($(_parent.element));
		});
	};

	Plugin.prototype.init = function () {
		if ($.trim(this.options.initialPath)!=""){
			this.navigateTo(this.options.initialPath);
		}
		else {
			this.navigateTo("/");
		}
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

})(jQuery, window, document );