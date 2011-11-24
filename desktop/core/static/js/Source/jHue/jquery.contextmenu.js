/*
* jHue contextMenu plugin
*/
;(function ($, window, document, undefined) {

	var pluginName = "jHueContextMenu",
	defaults = {
		on: "click",
		items: []
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
		$(this.element).mousedown(function(e){
			e.preventDefault();
			switch (e.which){
				case 1: 
					if (_this.options.on == "click"){
						$("#jHueContextMenu").toggle().css({
							left: e.pageX, 
							top: e.pageY
						});
						
					}
					break;
				case 3:
					if (_this.options.on == "rightClick"){
					}
					break;
			}
		});
		var _ctx;
		if ($("#jHueContextMenu").length == 0){
			_ctx = $("<ul>");
			_ctx.attr("id","jHueContextMenu");
			_ctx.addClass("dropdown-menu").addClass("contextMenu");
			_ctx.appendTo("body");
		}
		else {
			_ctx = $("#jHueContextMenu");
			_ctx.empty();
		}
		_ctx.hide();
		$(this.options.items).each(function(cnt, item){
			var _item = $("<li>");
			if (item.divider){
				_item.addClass("divider");
			}
			else {
				var _link = $("<a>").text(item.text).attr("href","javascript:void(0)");
				_link.appendTo(_item);
				if (item.onSelect){
					_link.click(function(){
						item.onSelect();
						_ctx.hide();
					});
				}
			}
			_item.appendTo(_ctx);
		});

		$("body").click(function(){
//			console.log(_ctx.is(":visible"));
		});
			

		
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
