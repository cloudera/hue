/*! selectize clear button plugin by Alexey Petushkov | https://github.com/mentatxx/selectize-plugin-clear | Apache License (v2) */

Selectize.define('clear_button', function (options) {
    /**
     * Escapes a string for use within HTML.
     *
     * @param {string} str
     * @returns {string}
     */
    var escape_html = function (str) {
        return (str + '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    };

    options = $.extend({
        label: '&times;',
        title: 'Remove',
        className: 'clearAll',
        append: true,
        hideWhenEmpty: true,
        leaveOpen: false
    }, options);

    var self = this,
        $html = $('<span class="' +
            options.className +
            '" tabindex="-1" title="' +
            escape_html(options.title) +
            '">' +
            options.label +
            '</span>');


    this.setup = (function () {
        var original = self.setup;
        return function () {
            // override the item rendering method to add the button to each
            original.apply(this, arguments);

            this.$wrapper.append($html);

            if (options.hideWhenEmpty) {
                var $input = this.$input;
                var hideShowClrBtn = function ($inpt) {
                    var val = $inpt.val();
                    if (val) {
                        $html.show();
                    } else {
                        $html.hide();
                    }
                }

                hideShowClrBtn($input);
                $input.change(function () {
                    hideShowClrBtn($input);
                });
            }

            // add event listener
            this.$wrapper.on('click', '.' + options.className, function (e) {
                e.preventDefault();
                if (self.isLocked) return;
                self.clear();

                if (options.leaveOpen) {
                    self.$control_input.focus();
                }
            });
        };
    })();
});