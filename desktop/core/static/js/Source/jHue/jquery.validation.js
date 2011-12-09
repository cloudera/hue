/*
* jHue validation plugin
*/
;(function ($, window, document, undefined) {

	var pluginName = "jHueValidation",
	defaults = {
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
