
(function($) {
  "use strict";  // jshint;_;

  // save the original plugin function object
  var _super = $.fn.popover;

  // create a new constructor
  var Popover = function(element, options) {
    _super.Constructor.apply(this, arguments);
  };

  // extend prototypes and create a super function
  Popover.prototype = $.extend({}, _super.Constructor.prototype, {
    constructor: Popover,
    _super: function() {
      var args = $.makeArray(arguments);
      _super.Constructor.prototype[args.shift()].apply(this, args);
    },
    show: function() {
      var $tip, inside, pos, actualWidth, actualHeight, placement, tp;
      
      if (this.hasContent && this.enabled) {
        $tip = this.tip();
        this.setContent();
      
        if (this.options.animation) {
          $tip.addClass('fade');
        }
      
        placement = typeof this.options.placement == 'function' ?
          this.options.placement.call(this, $tip[0], this.$element[0]) :
          this.options.placement;
      
        inside = /in/.test(placement);

        $tip
          .remove()
          .css({ top: 0, left: 0, display: 'block' })
          .appendTo(inside ? this.$element : document.body);
      
        pos = this.getPosition(inside);

        actualWidth = $tip[0].offsetWidth;
        actualHeight = $tip[0].offsetHeight;
      
        switch (inside ? placement.split(' ')[1] : placement) {
          case 'bottom':
            tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - actualWidth / 2};
            break;
          case 'top':
            tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2};
            break;
          case 'left':
            tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth};
            break;
          case 'right':
            tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width};
            break;

          // extend placements (top)
          case 'topLeft':
            tp = {top: pos.top - actualHeight,  left: pos.left + pos.width / 2 - (actualWidth * .25)};
            break;
          case 'topRight':
            tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - (actualWidth * .75)};
            break;

          // extend placements (right)
          case 'rightTop':
            tp = {top: pos.top + pos.height / 2 - (actualHeight *.25), left: pos.left + pos.width};
            break;
          case 'rightBottom':
            tp = {top: pos.top + pos.height / 2 - (actualHeight * .75), left: pos.left + pos.width};
            break;

          // extend placements (bottom)
          case 'bottomLeft':
            tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - (actualWidth * .25)};
            break;
          case 'bottomRight':
            tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - (actualWidth * .80)};
            break;

          // extend placements (left)
          case 'leftTop':
            tp = {top: pos.top + pos.height / 2 - (actualHeight *.25), left: pos.left - actualWidth};
            break;
          case 'leftBottom':
            tp = {top: pos.top + pos.height / 2 - (actualHeight * .75), left: pos.left - actualWidth};
            break;

        }
      
        $tip
          .css(tp)
          .addClass(placement)
          .addClass('in');
      }
    }
  });

  $.fn.popover = $.extend(function (option) {
    return this.each(function () {
      var $this = $(this)
        , data = $this.data('popover')
        , options = typeof option == 'object' && option;
      if (!data) $this.data('popover', (data = new Popover(this, options)));
      if (typeof option == 'string') data[option]();
    });
  }, _super);

})(jQuery);