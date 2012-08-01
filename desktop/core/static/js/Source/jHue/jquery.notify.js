/*
* jHue notify plugin
* 
*/
;(function ($, window, document, undefined) {

	var pluginName = "jHueNotify",
    TYPES = {
        INFO: "INFO",
        ERROR: "ERROR",
        GENERAL: "GENERAL"
    },
	defaults = {
        level: TYPES.GENERAL,
        message: "",
        sticky: false,
        css: null
    };

	function Plugin(options) {
		this.options = $.extend({}, defaults, options) ;
		this._defaults = defaults;
		this._name = pluginName;
		this.show();
	}
	
	Plugin.prototype.setOptions = function(options) {
		this.options = $.extend({}, defaults, options) ;
	};

	Plugin.prototype.show = function () {
		var _this = this;		
        var el = $("#jHueNotify");
        // stops all the current animations and resets the style
        el.stop(true);
        el.attr("class", "alert");
        el.find(".close").hide();

        el.click(function(){
            $(this).stop(true);
            $(this).fadeOut();
        });

        if (_this.options.level == TYPES.ERROR){
            el.addClass("alert-error");
            el.find(".message").html("<i class='icon-warning-sign'></i> <strong>" + _this.options.message + "</strong>");
        }
        else if (_this.options.level == TYPES.INFO){
            el.addClass("alert-info");
            el.find(".message").html("<i class='icon-info-sign'></i> <strong>" + _this.options.message + "</strong>");
        }
        else {
            el.find(".message").html(_this.options.message);
        }

        if (_this.options.css != null){
            el.attr("style", _this.options.css);
        }

        if (_this.options.sticky){
            el.find(".close").click(function(){
                el.fadeOut();
            }).show();
            el.show();
        }
        else {
            el.show().animate({
                opacity: 1
            }, 3000, function(){
                el.fadeOut();
            });
        }
	};

    $[pluginName] = function () {
    };

    $[pluginName].info = function (message) {
        new Plugin({ level: TYPES.INFO, message: message});
    };

    $[pluginName].error = function (message) {
        new Plugin({ level: TYPES.ERROR, message: message, sticky: true});
    };

    $[pluginName].notify = function (options) {
        new Plugin(options);
    };

})(jQuery, window, document);
