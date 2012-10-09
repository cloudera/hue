/*
 * jHue table scroller plugin
 *
 */
;
(function ($, window, document, undefined) {

    var pluginName = "jHueTableScroller",
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

        resizeScrollingTable(_this.element);

        $(window).resize(function () {
            resizeScrollingTable(_this.element);
        });

        function resizeScrollingTable(el) {
            $(el).css("overflow-y", "").css("height", "");
            var heightAfter = 0;
            $(el).nextAll(":visible").each(function () {
                heightAfter += $(this).outerHeight(true);
            });
            if ($(el).height() > ($(window).height() - $(el).offset().top - heightAfter)) {
                $(el).css("overflow-y", "auto").height($(window).height() - $(el).offset().top - heightAfter);
            }
        }
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
