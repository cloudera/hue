/*
 * jHue row selector plugin
 *
 */
;
(function ($, window, document, undefined) {

    var pluginName = "jHueRowSelector",
        defaults = {
        };

    function Plugin(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options);
        this._defaults = defaults;
        this._name = pluginName;
        this.init();
    }

    Plugin.prototype.setOptions = function (options) {
        this.options = $.extend({}, defaults, options);
    };

    Plugin.prototype.init = function () {
        var _this = this;
        $(_this.element).closest("tr").click(function (e) {
            if ($(e.target).data("row-selector-exclude")) {
                return;
            }
            if (!$(e.target).is("a")) {
                if ($.trim($(_this.element).attr("href")) != "" && $.trim($(_this.element).attr("href")) != "#") {
                    location.href = $(_this.element).attr("href");
                }
                else {
                    $(_this.element).click();
                }
            }
        }).css("cursor", "pointer");
    };

    $.fn[pluginName] = function (options) {
        return this.each(function () {
            if (!$.data(this, 'plugin_' + pluginName)) {
                $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
            }
            else {
                $.data(this, 'plugin_' + pluginName).setOptions(options);
            }
        });
    }

})(jQuery, window, document);
