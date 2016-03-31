// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
 * jHue horizontal scrollbar for dataTables_wrapper
 *
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueHorizontalScrollbar",
    defaults = {};

  function Plugin(element, options) {
    this.element = element;
    this.options = $.extend({}, defaults, options);
    this._defaults = defaults;
    this._name = pluginName;
    this.init();
  }

  Plugin.prototype.init = function () {
    var el = this.element;
    if ($(el).parents('.dataTables_wrapper').length > 0) {
      var scrollingRatio = function () {
        return $(el).parents('.dataTables_wrapper').width() - $(el).parents('.dataTables_wrapper').find('hue-scrollbar-x').width()
      };
      if ($(el).parents('.dataTables_wrapper').find('.hue-scrollbar-x-rail').length == 0 && $(el).parents('.dataTables_wrapper').width() < $(el).parents('.dataTables_wrapper')[0].scrollWidth) {
        var colWidth = $(el).parents('.dataTables_wrapper').find('.jHueTableExtenderClonedContainerColumn').width() + 5;
        var scrollbarRail = $('<div>');
        var scrollbar = $('<div>').addClass('hue-scrollbar-x');
        scrollbar.width(Math.max(20, $(el).parents('.dataTables_wrapper').width() * ($(el).parents('.dataTables_wrapper').width() / $(el).parents('.dataTables_wrapper')[0].scrollWidth)));
        scrollbar.appendTo(scrollbarRail);
        scrollbar.draggable({
          axis: 'x',
          containment: 'parent',
          drag: function (e, ui) {
            $(el).parents('.dataTables_wrapper').scrollLeft(($(el).parents('.dataTables_wrapper')[0].scrollWidth - $(el).parents('.dataTables_wrapper').width()) * (ui.position.left / (scrollbarRail.width() - $(this).width())))
          }
        });
        $(el).parents('.dataTables_wrapper').bind('mousewheel DOMMouseScroll wheel', function (e) {
          var _e = e.originalEvent,
            _deltaX = _e.wheelDeltaX || -_e.deltaX,
            _deltaY = _e.wheelDeltaY || -_e.deltaY;
          if (Math.abs(_deltaX) > Math.abs(_deltaY)) {
            this.scrollLeft += -_deltaX / 2;
            e.stopPropagation();
            e.stopImmediatePropagation();
            scrollbar.css("left", ((scrollbarRail.width() - scrollbar.width()) * ($(el).parents('.dataTables_wrapper').scrollLeft() / ($(el).parents('.dataTables_wrapper')[0].scrollWidth - $(el).parents('.dataTables_wrapper').width()))) + "px");
          }
          e.preventDefault();
        });
        scrollbarRail.addClass('hue-scrollbar-x-rail').appendTo($(el).parents(".dataTables_wrapper"));
        scrollbarRail.width($(el).parents(".dataTables_wrapper").width() - colWidth);
        scrollbarRail.css("marginLeft", (colWidth) + "px");
      }
      else {
        var colWidth = $(el).parents('.dataTables_wrapper').find('.jHueTableExtenderClonedContainerColumn').width() + 5;
        $(el).parents('.dataTables_wrapper').find('.hue-scrollbar-x-rail').width($(el).parents(".dataTables_wrapper").width() - colWidth);
        var scrollbarRail = $(el).parents('.dataTables_wrapper').find('.hue-scrollbar-x-rail');
        var scrollbar = $(el).parents('.dataTables_wrapper').find('.hue-scrollbar-x');
        scrollbar.width(Math.max(20, $(el).parents('.dataTables_wrapper').width() * ($(el).parents('.dataTables_wrapper').width() / $(el).parents('.dataTables_wrapper')[0].scrollWidth)));
        scrollbar.css("left", ((scrollbarRail.width() - scrollbar.width()) * ($(el).parents('.dataTables_wrapper').scrollLeft() / ($(el).parents('.dataTables_wrapper')[0].scrollWidth - $(el).parents('.dataTables_wrapper').width()))) + "px");
      }
    }
  };

  $.fn[pluginName] = function (options) {
    return this.each(function () {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    });
  }

})(jQuery, window, document);
