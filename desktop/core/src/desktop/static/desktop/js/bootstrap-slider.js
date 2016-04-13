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

(function ($) {

  var ErrorMsgs = {
    formatInvalidInputErrorMsg: function (input) {
      return "Invalid input value '" + input + "' passed in";
    },
    callingContextNotSliderInstance: "Calling context element does not have instance of Slider bound to it. Check your code to make sure the JQuery object returned from the call to the slider() initializer is calling the method"
  };

  var Slider = function (element, options) {
    var el = this.element = $(element).hide();
    var updateSlider = false;
    var parent = this.element.parent();

    if (parent.hasClass("slider") === true) {
      updateSlider = true;
      this.picker = parent;
    }
    else {
      this.picker = $('<div class="slider">' +
        '<div class="slider-track">' +
        '<div class="slider-selection"></div>' +
        '<div class="slider-handle"></div>' +
        '<div class="slider-handle"></div>' +
        '</div>' +
        '<div id="tooltip" class="tooltip"><div class="tooltip-arrow"></div><input type="text" class="tooltip-inner" /></div>' +
        '<div id="tooltip_start" class="tooltip"><input type="text" class="tooltip-inner" style="margin-bottom: -14px!important" /></div>' +
        '<div id="tooltip_end" class="tooltip"><input type="text" class="tooltip-inner" style="margin-bottom: -14px!important" /></div>' +
        '<div id="tooltip_min" class="tooltip"><div class="tooltip-arrow"></div><input type="text" class="tooltip-inner subtle" /></div>' +
        '<div id="tooltip_max" class="tooltip"><div class="tooltip-arrow"></div><input type="text" class="tooltip-inner subtle" /></div>' +
        '<div id="tooltip_step" class="tooltip"><div style="text-align: center;height: 11px;"><i class="fa fa-arrows-h"></i></div><input type="text" class="tooltip-inner subtle" title="' + options.labels.STEP + '" /></div>' +
        '</div>')
        .insertBefore(this.element)
        .append(this.element);
    }

    this.id = this.element.data("slider-id") || options.id;
    if (this.id) {
      this.picker[0].id = this.id;
    }

    if (("ontouchstart" in window) || window.DocumentTouch && document instanceof window.DocumentTouch) {
      this.touchCapable = true;
    }

    var tooltip = this.element.data("slider-tooltip") || options.tooltip;

    this.tooltip = this.picker.find("#tooltip");
    this.tooltipInner = this.tooltip.find("input.tooltip-inner");

    this.tooltip_start = this.picker.find("#tooltip_start");
    this.tooltipInner_start = this.tooltip_start.find("input.tooltip-inner");

    this.tooltip_end = this.picker.find("#tooltip_end");
    this.tooltipInner_end = this.tooltip_end.find("input.tooltip-inner");

    this.tooltip_min = this.picker.find("#tooltip_min");
    this.tooltipInner_min = this.tooltip_min.find("input.tooltip-inner");

    this.tooltip_max = this.picker.find("#tooltip_max");
    this.tooltipInner_max = this.tooltip_max.find("input.tooltip-inner");

    this.tooltip_step = this.picker.find("#tooltip_step");
    this.tooltipInner_step = this.tooltip_step.find("input.tooltip-inner");

    if (updateSlider === true) {
      // Reset classes
      this.picker.removeClass("slider-horizontal");
      this.picker.removeClass("slider-vertical");
      this.tooltip.removeClass("hide");
      this.tooltip_start.removeClass("hide");
      this.tooltip_end.removeClass("hide");
      this.tooltip_min.removeClass("hide");
      this.tooltip_max.removeClass("hide");
      this.tooltip_step.removeClass("hide");
    }

    this.picker
      .addClass("slider-horizontal")
    this.picker.width(Math.min(this.element.parents(".card-widget").innerWidth() - 60, 250));
    this.stylePos = "left";
    this.mousePos = "pageX";
    this.sizePos = "offsetWidth";
    this.tooltip.addClass("top")[0].style.top = -this.tooltip.outerHeight() - 14 + "px";
    this.tooltip_start.addClass("top")[0].style.top = "-30px";
    this.tooltip_end.addClass("top")[0].style.top = "-30px";
    this.tooltip_min.addClass("top")[0].style.top = "18px";
    this.tooltip_max.addClass("top")[0].style.top = "18px";
    this.tooltip_step.addClass("top")[0].style.top = "6px";

    this.tooltipInner_start.on({
      blur: $.proxy(this.blur, this, 0),
      focus: $.proxy(this.focus, this, 0),
      keydown: $.proxy(this.inputKeydown, this, 0)
    });

    this.tooltipInner_end.on({
      blur: $.proxy(this.blur, this, 0),
      focus: $.proxy(this.focus, this, 0),
      keydown: $.proxy(this.inputKeydown, this, 0)
    });

    this.tooltipInner_min.on({
      blur: $.proxy(this.blur, this, 0),
      focus: $.proxy(this.focus, this, 0),
      keydown: $.proxy(this.inputKeydown, this, 0)
    });

    this.tooltipInner_max.on({
      blur: $.proxy(this.blur, this, 0),
      focus: $.proxy(this.focus, this, 0),
      keydown: $.proxy(this.inputKeydown, this, 0)
    });

    this.tooltipInner_step.on({
      blur: $.proxy(this.blur, this, 0),
      focus: $.proxy(this.focus, this, 0),
      keydown: $.proxy(this.inputKeydown, this, 0)
    });


    var self = this;
    $.each([
      "type",
      "min",
      "max",
      "step",
      "precision",
      "value",
      "start",
      "end",
      "reversed",
      "handle"
    ], function (i, attr) {
      if (typeof el.data("slider-" + attr) !== "undefined") {
        self[attr] = el.data("slider-" + attr);
      }
      else if (typeof options[attr] !== "undefined") {
        self[attr] = options[attr];
      }
      else if (typeof el.prop(attr) !== "undefined") {
        self[attr] = el.prop(attr);
      }
      else {
        self[attr] = 0; // to prevent empty string issues in calculations in IE
      }
    });

    this.value = [this.start, this.end];
    this.range = true;


    this.selection = this.element.data("slider-selection") || options.selection;
    this.selectionEl = this.picker.find(".slider-selection");
    if (this.selection === "none") {
      this.selectionEl.addClass("hide");
    }

    this.selectionElStyle = this.selectionEl[0].style;

    this.handle1 = this.picker.find(".slider-handle:first");
    this.handle1Stype = this.handle1[0].style;

    this.handle2 = this.picker.find(".slider-handle:last");
    this.handle2Stype = this.handle2[0].style;

    if (updateSlider === true) {
      // Reset classes
      this.handle1.removeClass("round triangle");
      this.handle2.removeClass("round triangle hide");
    }

    switch (this.handle) {
      case "round":
        this.handle1.addClass("round");
        this.handle2.addClass("round");
        break;
      case "triangle":
        this.handle1.addClass("triangle");
        this.handle2.addClass("triangle");
        break;
    }

    this.offset = this.picker.offset();
    this.size = this.picker[0][this.sizePos];
    this.formatter = options.formatter;
    this.stepFormatter = options.stepFormatter;

    this.reverseFormatter = options.reverseFormatter;
    this.reverseStepFormatter = options.reverseStepFormatter;

    this.tooltip_separator = options.tooltip_separator;
    this.tooltip_split = options.tooltip_split;

    this.setValue(this.value);

    this.handle1.on({
      keydown: $.proxy(this.keydown, this, 0)
    });
    this.handle2.on({
      keydown: $.proxy(this.keydown, this, 1)
    });

    if (this.touchCapable) {
      // Touch: Bind touch events:
      this.picker.on({
        touchstart: $.proxy(this.mousedown, this)
      });
    }
    // Bind mouse events:
    this.picker.find(".slider-track").on({
      mousedown: $.proxy(this.mousedown, this)
    });

    if (tooltip === "hide") {
      this.tooltip.addClass("hide");
      this.tooltip_start.addClass("hide");
      this.tooltip_end.addClass("hide");
    }
    else if (tooltip === "always") {
      this.showTooltip();
      this.alwaysShowTooltip = true;
    }
    else {
      this.picker.on({
        mouseenter: $.proxy(this.showTooltip, this),
        mouseleave: $.proxy(this.hideTooltip, this)
      });
      this.handle1.on({
        focus: $.proxy(this.showTooltip, this),
        blur: $.proxy(this.hideTooltip, this)
      });
      this.handle2.on({
        focus: $.proxy(this.showTooltip, this),
        blur: $.proxy(this.hideTooltip, this)
      });
    }

    this.enabled = options.enabled && (this.element.data("slider-enabled") === undefined || this.element.data("slider-enabled") === true);
    if (this.enabled) {
      this.enable();
    }
    else {
      this.disable();
    }
    this.natural_arrow_keys = this.element.data("slider-natural_arrow_keys") || options.natural_arrow_keys;
    this.layout();

    var _self = this;
    var _resizeTimeout = -1;
    $(window).on("resize", function(){
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(function(){
        _self.layout();
      }, 300);
    });
  };

  Slider.prototype = {
    constructor: Slider,

    over: false,
    inDrag: false,

    showTooltip: function () {
      if (this.tooltip_split === false) {
        this.tooltip.addClass("in");
      }
      else {
        this.tooltip_start.addClass("in");
        this.tooltip_end.addClass("in");
        this.tooltip_min.addClass("in");
        this.tooltip_max.addClass("in");
        this.tooltip_step.addClass("in");
      }

      this.over = true;
    },

    hideTooltip: function () {
      if (this.inDrag === false && this.alwaysShowTooltip !== true) {
        this.tooltip.removeClass("in");
        this.tooltip_start.removeClass("in");
        this.tooltip_end.removeClass("in");
        this.tooltip_min.removeClass("in");
        this.tooltip_max.removeClass("in");
        this.tooltip_step.removeClass("in");
      }
      this.over = false;
    },

    layout: function () {
      var positionPercentages;

      this.picker.width(Math.min(this.element.parents(".card-widget").innerWidth() - 60, 250));
      this.size = this.picker[0][this.sizePos];

      if (this.reversed) {
        positionPercentages = [ 100 - this.percentage[0], this.percentage[1] ];
      }
      else {
        positionPercentages = [ this.percentage[0], this.percentage[1] ];
      }

      this.handle1Stype[this.stylePos] = positionPercentages[0] + "%";
      this.handle2Stype[this.stylePos] = positionPercentages[1] + "%";

      this.selectionElStyle.left = Math.min(positionPercentages[0], positionPercentages[1]) + "%";
      this.selectionElStyle.width = Math.abs(positionPercentages[0] - positionPercentages[1]) + "%";

      this.tooltip_min.addClass("bottom");
      this.tooltip_max.addClass("bottom");
      this.tooltip_step.addClass("bottom");

      if (this.range) {
        this.tooltipInner.val(
          this.formatter(this.value[0]) + this.tooltip_separator + this.formatter(this.value[1])
        );
        this.tooltip[0].style[this.stylePos] = this.size * (positionPercentages[0] + (positionPercentages[1] - positionPercentages[0]) / 2) / 100 - (this.tooltip.outerWidth() / 2) + "px";

        this.tooltipInner_start.val(
          this.formatter(this.value[0])
        );
        this.tooltipInner_end.val(
          this.formatter(this.value[1])
        );

        this.tooltipInner_min.val(
          this.formatter(this.min)
        );
        this.tooltipInner_max.val(
          this.formatter(this.max)
        );
        this.tooltipInner_step.val(
          this.stepFormatter(this.step)
        );

        this.tooltip_start[0].style[this.stylePos] = this.size * ( (positionPercentages[0]) / 100) - (this.tooltip_start.outerWidth() / 2) + "px";
        this.tooltip_end[0].style[this.stylePos] = this.size * ( (positionPercentages[1]) / 100) - (this.tooltip_end.outerWidth() / 2) + "px";

        this.tooltip_min[0].style[this.stylePos] = -(this.tooltip_min.outerWidth() / 2) + "px";
        this.tooltip_max[0].style[this.stylePos] = this.size - (this.tooltip_max.outerWidth() / 2) + "px";
        this.tooltip_step[0].style[this.stylePos] = this.size/2 - (this.tooltip_max.outerWidth() / 2) + "px";

      }
      else {
        this.tooltipInner.val(
          this.formatter(this.value[0])
        );
        this.tooltip[0].style[this.stylePos] = this.size * positionPercentages[0] / 100 - (this.tooltip.outerWidth() / 2) + "px";
      }
    },

    blur: function (idx, ev) {
      this.value[0] = this.reverseFormatter(this.tooltipInner_start.val());
      this.value[1] = this.reverseFormatter(this.tooltipInner_end.val());
      this.setAdditionalValues();
      this.setValue(this.value, true, true);
    },

    focus: function (idx, ev) {
      $(".slider .tooltip").css("zIndex", 10);
      $(ev.target).parent().css("zIndex", 20);
    },

    inputKeydown: function (idx, ev) {
      if (ev.which == 13) {
        this.blur(ev);
      }
    },

    mousedown: function (ev) {
      if (!this.isEnabled()) {
        return false;
      }
      // Touch: Get the original event:
      if (this.touchCapable && ev.type === "touchstart") {
        ev = ev.originalEvent;
      }

      this.triggerFocusOnHandle();

      this.offset = this.picker.offset();
      this.size = this.picker[0][this.sizePos];

      var percentage = this.getPercentage(ev);

      if (this.range) {
        var diff1 = Math.abs(this.percentage[0] - percentage);
        var diff2 = Math.abs(this.percentage[1] - percentage);
        this.dragged = (diff1 < diff2) ? 0 : 1;
      }
      else {
        this.dragged = 0;
      }

      $(".slider .tooltip").css("zIndex", 10);
      if (this.dragged == 0){
        $("#tooltip_start").css("zIndex", 20);
      }
      else {
        $("#tooltip_end").css("zIndex", 20);
      }

      this.percentage[this.dragged] = this.reversed ? 100 - percentage : percentage;
      this.layout();

      if (this.touchCapable) {
        // Touch: Bind touch events:
        $(document).on({
          touchmove: $.proxy(this.mousemove, this),
          touchend: $.proxy(this.mouseup, this)
        });
      }
      // Bind mouse events:
      $(document).on({
        mousemove: $.proxy(this.mousemove, this),
        mouseup: $.proxy(this.mouseup, this)
      });

      this.inDrag = true;
      var val = this.calculateValue();
      this.element.trigger({
        type: "slideStart",
        value: val
      })
        .data("value", val)
        .prop("value", val);
      this.setAdditionalValues();
      this.setValue(val);
      return true;
    },

    triggerFocusOnHandle: function (handleIdx) {
      if (handleIdx === 0) {
        this.handle1.focus();
      }
      if (handleIdx === 1) {
        this.handle2.focus();
      }
    },

    keydown: function (handleIdx, ev) {
      if (!this.isEnabled()) {
        return false;
      }

      var dir;
      switch (ev.which) {
        case 37: // left
        case 40: // down
          dir = -1;
          break;
        case 39: // right
        case 38: // up
          dir = 1;
          break;
      }
      if (!dir) {
        return;
      }

      // use natural arrow keys instead of from min to max
      if (this.natural_arrow_keys) {
        if (this.reversed) {
          dir = dir * -1;
        }
      }

      var oneStepValuePercentageChange = dir * this.percentage[2];
      var percentage = this.percentage[handleIdx] + oneStepValuePercentageChange;

      if (percentage > 100) {
        percentage = 100;
      }
      else if (percentage < 0) {
        percentage = 0;
      }

      this.dragged = handleIdx;
      this.adjustPercentageForRangeSliders(percentage);
      this.percentage[this.dragged] = percentage;
      this.layout();

      var val = this.calculateValue();

      this.element.trigger({
        type: "slideStart",
        value: val
      })
        .data("value", val)
        .prop("value", val);

      this.setAdditionalValues();
      this.setValue(val, true);

      this.element
        .trigger({
          type: "slideStop",
          value: val
        })
        .data("value", val)
        .prop("value", val);
      return false;
    },

    mousemove: function (ev) {
      if (!this.isEnabled()) {
        return false;
      }
      // Touch: Get the original event:
      if (this.touchCapable && ev.type === "touchmove") {
        ev = ev.originalEvent;
      }

      var percentage = this.getPercentage(ev);
      this.adjustPercentageForRangeSliders(percentage);
      this.percentage[this.dragged] = this.reversed ? 100 - percentage : percentage;
      this.layout();

      var val = this.calculateValue();
      this.setAdditionalValues();
      this.setValue(val, true);

      return false;
    },
    adjustPercentageForRangeSliders: function (percentage) {
      if (this.range) {
        if (this.dragged === 0 && this.percentage[1] < percentage) {
          this.percentage[0] = this.percentage[1];
          this.dragged = 1;
        }
        else if (this.dragged === 1 && this.percentage[0] > percentage) {
          this.percentage[1] = this.percentage[0];
          this.dragged = 0;
        }
      }
    },

    mouseup: function () {
      if (!this.isEnabled()) {
        return false;
      }
      if (this.touchCapable) {
        // Touch: Unbind touch event handlers:
        $(document).off({
          touchmove: this.mousemove,
          touchend: this.mouseup
        });
      }
      // Unbind mouse event handlers:
      $(document).off({
        mousemove: this.mousemove,
        mouseup: this.mouseup
      });

      this.inDrag = false;
      if (this.over === false) {
        this.hideTooltip();
      }
      var val = this.calculateValue();
      this.layout();
      this.element
        .data("value", val)
        .prop("value", val)
        .trigger({
          type: "slideStop",
          value: val
        });
      return false;
    },

    calculateValue: function () {
      var val;
      if (this.range) {
        val = [this.min, this.max];
        if (this.percentage[0] !== 0) {
          val[0] = (Math.max(this.min, this.min + Math.round((this.diff * this.percentage[0] / 100) / this.step) * this.step));
          val[0] = this.applyPrecision(val[0]);
        }
        if (this.percentage[1] !== 100) {
          val[1] = (Math.min(this.max, this.min + Math.round((this.diff * this.percentage[1] / 100) / this.step) * this.step));
          val[1] = this.applyPrecision(val[1]);
        }
        this.value = val;
      }
      else {
        val = (this.min + Math.round((this.diff * this.percentage[0] / 100) / this.step) * this.step);
        if (val < this.min) {
          val = this.min;
        }
        else if (val > this.max) {
          val = this.max;
        }
        val = parseFloat(val);
        val = this.applyPrecision(val);
        this.value = [val, this.value[1]];
      }
      return val;
    },
    applyPrecision: function (val) {
      var precision = this.precision || this.getNumDigitsAfterDecimalPlace(this.step);
      return this.applyToFixedAndParseFloat(val, precision);
    },
    /*
     Credits to Mike Samuel for the following method!
     Source: http://stackoverflow.com/questions/10454518/javascript-how-to-retrieve-the-number-of-decimals-of-a-string-number
     */
    getNumDigitsAfterDecimalPlace: function (num) {
      var match = ('' + num).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
      if (!match) {
        return 0;
      }
      return Math.max(0, (match[1] ? match[1].length : 0) - (match[2] ? +match[2] : 0));
    },

    applyToFixedAndParseFloat: function (num, toFixedInput) {
      var truncatedNum = num.toFixed(toFixedInput);
      return parseFloat(truncatedNum);
    },

    getPercentage: function (ev) {
      if (this.touchCapable && (ev.type === "touchstart" || ev.type === "touchmove")) {
        ev = ev.touches[0];
      }
      var percentage = (ev[this.mousePos] - this.offset[this.stylePos]) * 100 / this.size;
      percentage = Math.round(percentage / this.percentage[2]) * this.percentage[2];
      return Math.max(0, Math.min(100, percentage));
    },

    getValue: function () {
      if (this.range) {
        return this.value;
      }
      return this.value[0];
    },

    setAdditionalValues: function() {
      this.min = this.reverseFormatter(this.tooltipInner_min.val());
      this.max = this.reverseFormatter(this.tooltipInner_max.val());
      this.start = this.reverseFormatter(this.tooltipInner_start.val());
      this.end = this.reverseFormatter(this.tooltipInner_end.val());
      this.step = this.reverseStepFormatter(this.tooltipInner_step.val());
    },

    setValue: function (val, triggerSlideEvent, triggerSlideStopEvent) {
      if (!val) {
        val = 0;
      }
      this.value = this.validateInputValue(val);

      if (this.range) {
        this.value[0] = this.applyPrecision(this.value[0]);
        this.value[1] = this.applyPrecision(this.value[1]);

        this.value[0] = Math.max(this.min, Math.min(this.max, this.value[0]));
        this.value[1] = Math.max(this.min, Math.min(this.max, this.value[1]));
      }
      else {
        this.value = this.applyPrecision(this.value);
        this.value = [ Math.max(this.min, Math.min(this.max, this.value))];
        this.handle2.addClass("hide");
        if (this.selection === "after") {
          this.value[1] = this.max;
        }
        else {
          this.value[1] = this.min;
        }
      }

      this.diff = this.max - this.min;
      if (this.diff > 0) {
        this.percentage = [
          (this.value[0] - this.min) * 100 / this.diff,
          (this.value[1] - this.min) * 100 / this.diff,
          this.step * 100 / this.diff
        ];
      }
      else {
        this.percentage = [0, 0, 100];
      }

      this.layout();


      if (triggerSlideEvent === true) {
        var slideEventValue = this.range ? this.value : this.value[0];
        this.element
          .trigger({
            'type': "slide",
            'value': slideEventValue,
            'min': this.min,
            'max': this.max,
            'start': this.start,
            'end': this.end,
            'step': this.step
          })
          .data("value", this.value)
          .prop("value", this.value);
      }
      if (triggerSlideStopEvent === true) {
        var slideEventValue = this.range ? this.value : this.value[0];
        this.element
          .trigger({
            'type': "slideStop",
            'value': slideEventValue,
            'min': this.min,
            'max': this.max,
            'start': this.start,
            'end': this.end,
            'step': this.step
          })
          .data("value", this.value)
          .prop("value", this.value);
      }
    },

    validateInputValue: function (val) {
      if (typeof val === "number") {
        return val;
      }
      else if (val instanceof Array) {
        $.each(val, function (i, input) {
          if (typeof input !== "number") {
            throw new Error(ErrorMsgs.formatInvalidInputErrorMsg(input));
          }
        });
        return val;
      }
      else {
        throw new Error(ErrorMsgs.formatInvalidInputErrorMsg(val));
      }
    },

    destroy: function () {
      this.handle1.off();
      this.handle2.off();
      this.element.off().show().insertBefore(this.picker);
      this.picker.off().remove();
      $(this.element).removeData("slider");
    },

    disable: function () {
      this.enabled = false;
      this.handle1.removeAttr("tabindex");
      this.handle2.removeAttr("tabindex");
      this.picker.addClass("slider-disabled");
      this.element.trigger("slideDisabled");
    },

    enable: function () {
      this.enabled = true;
      this.handle1.attr("tabindex", 0);
      this.handle2.attr("tabindex", 0);
      this.picker.removeClass("slider-disabled");
      this.element.trigger("slideEnabled");
    },

    toggle: function () {
      if (this.enabled) {
        this.disable();
      }
      else {
        this.enable();
      }
    },

    isEnabled: function () {
      return this.enabled;
    },

    setAttribute: function (attribute, value) {
      this[attribute] = value;
    },

    getAttribute: function (attribute) {
      return this[attribute];
    }

  };

  var publicMethods = {
    getValue: Slider.prototype.getValue,
    setValue: Slider.prototype.setValue,
    setAttribute: Slider.prototype.setAttribute,
    getAttribute: Slider.prototype.getAttribute,
    destroy: Slider.prototype.destroy,
    disable: Slider.prototype.disable,
    enable: Slider.prototype.enable,
    toggle: Slider.prototype.toggle,
    isEnabled: Slider.prototype.isEnabled,
    redraw: Slider.prototype.layout
  };

  $.fn.slider = function (option) {
    if (typeof option === "string" && option !== "refresh") {
      var args = Array.prototype.slice.call(arguments, 1);
      return invokePublicMethod.call(this, option, args);
    }
    else {
      return createNewSliderInstance.call(this, option);
    }
  };

  function invokePublicMethod(methodName, args) {
    if (publicMethods[methodName]) {
      var sliderObject = retrieveSliderObjectFromElement(this);
      var result = publicMethods[methodName].apply(sliderObject, args);

      if (typeof result === "undefined") {
        return $(this);
      }
      else {
        return result;
      }
    }
    else {
      throw new Error("method '" + methodName + "()' does not exist for slider.");
    }
  }

  function retrieveSliderObjectFromElement(element) {
    var sliderObject = $(element).data("slider");
    if (sliderObject && sliderObject instanceof Slider) {
      return sliderObject;
    }
    else {
      throw new Error(ErrorMsgs.callingContextNotSliderInstance);
    }
  }

  function createNewSliderInstance(opts) {
    var $this = $(this);
    $this.each(function () {
      var $this = $(this),
        slider = $this.data("slider"),
        options = typeof opts === "object" && opts;

      // If slider already exists, use its attributes
      // as options so slider refreshes properly
      if (slider && !options) {
        options = {};

        $.each($.fn.slider.defaults, function (key) {
          options[key] = slider[key];
        });
      }

      $this.data("slider", (new Slider(this, $.extend({}, $.fn.slider.defaults, options))));
    });
    return $this;
  }

  $.fn.slider.defaults = {
    type: "number",
    min: 0,
    max: 10,
    step: 1,
    precision: 0,
    value: 5,
    range: false,
    selection: "before",
    tooltip: "show",
    tooltip_separator: ":",
    tooltip_split: false,
    natural_arrow_keys: false,
    handle: "round",
    reversed: false,
    enabled: true,
    formatter: function (value) {
      return value;
    },
    stepFormatter: function (value) {
      return value;
    },
    reverseFormatter: function (value) {
      return value*1;
    },
    reverseStepFormatter: function (value) {
      return value*1;
    },
    labels: {
      STEP: "Increment"
    }
  };

  $.fn.slider.Constructor = Slider;

})(window.jQuery);
