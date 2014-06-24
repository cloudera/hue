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

ko.bindingHandlers.slideVisible = {
  init: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).toggle(ko.unwrap(value));
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    ko.unwrap(value) ? $(element).slideDown(100) : $(element).slideUp(100);
  }
};

ko.bindingHandlers.fadeVisible = {
  init: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).toggle(ko.unwrap(value));
  },
  update: function (element, valueAccessor) {
    var value = valueAccessor();
    $(element).stop();
    ko.unwrap(value) ? $(element).fadeIn() : $(element).hide();
  }
};


ko.extenders.numeric = function (target, precision) {
  var result = ko.computed({
    read: target,
    write: function (newValue) {
      var current = target(),
          roundingMultiplier = Math.pow(10, precision),
          newValueAsNum = isNaN(newValue) ? 0 : parseFloat(+newValue),
          valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;

      if (valueToWrite !== current) {
        target(valueToWrite);
      } else {
        if (newValue !== current) {
          target.notifySubscribers(valueToWrite);
        }
      }
    }
  }).extend({ notify: 'always' });
  result(target());
  return result;
};

ko.bindingHandlers.freshereditor = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var _el = $(element);
    var options = $.extend(valueAccessor(), {});
    _el.html(options.data());
    _el.freshereditor({
      excludes: ['strikethrough', 'removeFormat', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
    });
    _el.freshereditor("edit", true);
    _el.on("mouseup", function () {
      storeSelection();
      updateValues();
    });

    var sourceDelay = -1;
    _el.on("keyup", function () {
      clearTimeout(sourceDelay);
      storeSelection();
      sourceDelay = setTimeout(function () {
        updateValues();
      }, 100);
    });

    $(".chosen-select").chosen({
      disable_search_threshold: 10,
      width: "75%"
    });

    $(document).on("addFieldToVisual", function (e, field) {
      _el.focus();
      pasteHtmlAtCaret("{{" + field.name() + "}}");
    });

    $(document).on("addFunctionToVisual", function (e, fn) {
      _el.focus();
      pasteHtmlAtCaret(fn);
    });

    function updateValues() {
      $("[data-template]")[0].editor.setValue(stripHtmlFromFunctions(_el.html()));
      valueAccessor().data(_el.html());
    }

    function storeSelection() {
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          range = sel.getRangeAt(0);
          _el.data("range", range);
        }
      }
      else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        _el.data("selection", document.selection);
      }
    }

    function pasteHtmlAtCaret(html) {
      var sel, range;
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          if (_el.data("range")) {
            range = _el.data("range");
          }
          else {
            range = sel.getRangeAt(0);
          }
          range.deleteContents();

          // Range.createContextualFragment() would be useful here but is
          // non-standard and not supported in all browsers (IE9, for one)
          var el = document.createElement("div");
          el.innerHTML = html;
          var frag = document.createDocumentFragment(), node, lastNode;
          while ((node = el.firstChild)) {
            lastNode = frag.appendChild(node);
          }
          range.insertNode(frag);

          // Preserve the selection
          if (lastNode) {
            range = range.cloneRange();
            range.setStartAfter(lastNode);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      } else if (document.selection && document.selection.type != "Control") {
        // IE < 9
        if (_el.data("selection")) {
          _el.data("selection").createRange().pasteHTML(html);
        }
        else {
          document.selection.createRange().pasteHTML(html);
        }
      }
    }
  }
};

ko.bindingHandlers.slider = {
  init: function (element, valueAccessor) {
    var _el = $(element);
    var _options = $.extend(valueAccessor(), {});
    _el.slider({
      min: _options.start() ? _options.start() : 0,
      max: _options.end() ? _options.end() : 10,
      step: _options.gap() ? _options.gap() : 1,
      handle: _options.handle ? _options.handle : 'triangle',
      start: _options.min(),
      end: _options.max(),
      tooltip_split: true,
      tooltip: 'always'
    });
    _el.on("slide", function (e) {
      _options.start(e.min);
      _options.end(e.max);
      _options.min(e.start);
      _options.max(e.end);
      _options.gap(e.step);
    });
    _el.on("slideStop", function (e) {
      viewModel.search();
    });
  },
  update: function (element, valueAccessor) {
    var _options = $.extend(valueAccessor(), {});
  }
}

ko.bindingHandlers.daterangepicker = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var DATE_FORMAT = "YYYY-MM-DD";
    var TIME_FORMAT = "HH:mm:ss";
    var DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT;

    var _el = $(element);
    var _options = $.extend(valueAccessor(), {});

    var _intervalOptions = [
      '<option value="+200MILLISECONDS">200ms</option>',
      '<option value="+1SECONDS">1s</option>',
      '<option value="+1MINUTES">1m</option>',
      '<option value="+5MINUTES">5m</option>',
      '<option value="+10MINUTES">10m</option>',
      '<option value="+30MINUTES">30m</option>',
      '<option value="+1HOURS">1h</option>',
      '<option value="+3HOURS">3h</option>',
      '<option value="+12HOURS">12h</option>',
      '<option value="+1DAYS">1d</option>',
      '<option value="+7DAYS">7d</option>',
      '<option value="+1MONTHS">1M</option>',
      '<option value="+6MONTHS">6M</option>',
      '<option value="+1YEARS">1y</option>'
    ];

    function enableOptions() {
      var _opts = [];
      var _tmp = $("<div>").html(_intervalOptions.join(""))
      $.each(arguments, function (cnt, item) {
        if (_tmp.find("option[value='+" + item + "']").length > 0) {
          _opts.push('<option value="+' + item + '">' + _tmp.find("option[value='+" + item + "']").eq(0).text() + '</option>');
        }
      });
      return _opts;
    }

    function renderOptions(opts) {
      var _html = "";
      for (var i = 0; i < opts.length; i++) {
        _html += opts[i];
      }
      _html += '<option value="">Custom</option>';
      return _html;
    }

    var _tmpl = $('<div class="simpledaterangepicker">' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-small form-control start-date" />' +
            '</div>' +
            '<div class="input-prepend input-group left-margin">' +
            '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
            '<input type="text" class="input-mini form-control start-time" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-small form-control end-date" />' +
            '</div>' +
            '<div class="input-prepend input-group left-margin">' +
            '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
            '<input type="text" class="input-mini form-control end-time" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.INTERVAL + '</div>' +
            '<select class="input-small interval-select" style="margin-right: 6px">' +
            renderOptions(_intervalOptions) +
            '</select>' +
            '<input class="input interval hide" type="text" value="" />' +
            '</div>' +
            '<div class="facet-field-cnt picker">' +
            '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
            '<div class="facet-field-switch"><a href="javascript:void(0)"><i class="fa fa-calendar-o"></i> ' + KO_DATERANGEPICKER_LABELS.CUSTOM_FORMAT + '</a></div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-large form-control start-date-custom" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
            '<input type="text" class="input-large form-control end-date-custom" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.INTERVAL + '</div>' +
            '<div class="input-prepend input-group">' +
            '<span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span>' +
            '<input type="text" class="input-large form-control interval-custom" />' +
            '</div>' +
            '</div>' +
            '<div class="facet-field-cnt custom">' +
            '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
            '<div class="facet-field-switch"><a href="javascript:void(0)"><i class="fa fa-calendar"></i> ' + KO_DATERANGEPICKER_LABELS.DATE_PICKERS + '</a></div>' +
            '</div>' +

            '</div>'
    );

    _tmpl.insertAfter(_el);

    var _minMoment = moment(_options.min());
    var _maxMoment = moment(_options.max());
    var _startMoment = moment(_options.start());
    var _endMoment = moment(_options.end());

    if (_minMoment.isValid()) {
      _tmpl.find(".facet-field-cnt.custom").hide();
      _tmpl.find(".facet-field-cnt.picker").show();
      _tmpl.find(".start-date").val(_minMoment.format(DATE_FORMAT));
      _tmpl.find(".start-time").val(_minMoment.format(TIME_FORMAT));
      _tmpl.find(".end-date").val(_maxMoment.format(DATE_FORMAT));
      _tmpl.find(".end-time").val(_maxMoment.format(TIME_FORMAT));
      _tmpl.find(".interval").val(_options.gap());
      _tmpl.find(".interval-custom").val(_options.gap());
    }
    else {
      _tmpl.find(".facet-field-cnt.custom").show();
      _tmpl.find(".facet-field-cnt.picker").hide();
      _tmpl.find(".start-date-custom").val(_options.min())
      _tmpl.find(".end-date-custom").val(_options.max())
      _tmpl.find(".interval-custom").val(_options.gap())
    }

    _tmpl.find(".start-date").datepicker({
      format: DATE_FORMAT.toLowerCase()
    }).on("changeDate", function () {
      rangeHandler(true);
    });

    _tmpl.find(".start-time").timepicker({
      minuteStep: 1,
      showSeconds: true,
      showMeridian: false,
      defaultTime: false
    });

    _tmpl.find(".end-date").datepicker({
      format: DATE_FORMAT.toLowerCase()
    }).on("changeDate", function () {
      rangeHandler(false);
    });

    _tmpl.find(".end-time").timepicker({
      minuteStep: 1,
      showSeconds: true,
      showMeridian: false,
      defaultTime: false
    });

    _tmpl.find(".start-time").on("change", function () {
      // the timepicker plugin doesn't have a change event handler
      // so we need to wait a bit to handle in with the default field event
      window.setTimeout(function () {
        rangeHandler(true)
      }, 200);
    });

    _tmpl.find(".end-time").on("change", function () {
      window.setTimeout(function () {
        rangeHandler(false)
      }, 200);
    });

    if (_minMoment.isValid()) {
      rangeHandler(true);
    }

    _tmpl.find(".facet-field-cnt.picker .facet-field-switch a").on("click", function () {
      _tmpl.find(".facet-field-cnt.custom").show();
      _tmpl.find(".facet-field-cnt.picker").hide();
    });

    _tmpl.find(".facet-field-cnt.custom .facet-field-switch a").on("click", function () {
      _tmpl.find(".facet-field-cnt.custom").hide();
      _tmpl.find(".facet-field-cnt.picker").show();
    });

    _tmpl.find(".start-date-custom").on("change", function () {
      _options.min(_tmpl.find(".start-date-custom").val());
      _options.start(_options.min());
    });

    _tmpl.find(".end-date-custom").on("change", function () {
      _options.max(_tmpl.find(".end-date-custom").val());
      _options.end(_options.max());
    });

    _tmpl.find(".interval-custom").on("change", function () {
      _options.gap(_tmpl.find(".interval-custom").val());
    });

    function matchIntervals() {
      if (_tmpl.find(".interval-select option[value='" + _options.gap() + "']").length > 0) {
        _tmpl.find(".interval-select").val(_options.gap());
        _tmpl.find(".interval").hide();
      }
      else {
        _tmpl.find(".interval-select").val("");
        _tmpl.find(".interval").show();
      }
    }

    _tmpl.find(".interval-select").on("change", function () {
      if (_tmpl.find(".interval-select").val() == "") {
        _tmpl.find(".interval").show();
      }
      else {
        _tmpl.find(".interval").hide();
        _options.gap(_tmpl.find(".interval-select").val());
        _tmpl.find(".interval").val(_options.gap());
      }
    });

    _tmpl.find(".interval").on("change", function () {
      if (_tmpl.find(".interval-select").val() == "") {
        _options.gap(_tmpl.find(".interval").val());
        _tmpl.find(".interval-custom").val(_options.gap());
      }
    });

    function rangeHandler(isStart) {
      var startDate = moment(_tmpl.find(".start-date").val() + " " + _tmpl.find(".start-time").val(), DATETIME_FORMAT);
      var endDate = moment(_tmpl.find(".end-date").val() + " " + _tmpl.find(".end-time").val(), DATETIME_FORMAT);
      if (startDate.valueOf() > endDate.valueOf()) {
        if (isStart) {
          _tmpl.find(".end-date").val(startDate.format(DATE_FORMAT));
          _tmpl.find(".end-date").datepicker('setValue', startDate.format(DATE_FORMAT));
          _tmpl.find(".end-date").data("original-val", _tmpl.find(".end-date").val());
          _tmpl.find(".end-time").val(startDate.format(TIME_FORMAT));
        }
        else {
          if (_tmpl.find(".end-date").val() == _tmpl.find(".start-date").val()) {
            _tmpl.find(".end-time").val(startDate.format(TIME_FORMAT));
            _tmpl.find(".end-time").data("timepicker").setValues(startDate.format(TIME_FORMAT));
          }
          else {
            _tmpl.find(".end-date").val(_tmpl.find(".end-date").data("original-val"));
            _tmpl.find(".end-date").datepicker("setValue", _tmpl.find(".end-date").data("original-val"));
          }
          // non-sticky error notification
          $.jHueNotify.notify({
            level: "ERROR",
            message: "The end cannot be before the starting moment"
          });
        }
      }
      else {
        _tmpl.find(".end-date").data("original-val", _tmpl.find(".end-date").val());
        _tmpl.find(".start-date").datepicker("hide");
        _tmpl.find(".end-date").datepicker("hide");
      }

      var _calculatedStartDate = moment(_tmpl.find(".start-date").val() + " " + _tmpl.find(".start-time").val(), DATETIME_FORMAT).utc();
      var _calculatedEndDate = moment(_tmpl.find(".end-date").val() + " " + _tmpl.find(".end-time").val(), DATETIME_FORMAT).utc();

      _options.min(_calculatedStartDate.format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      _options.start(_options.min());
      _options.max(_calculatedEndDate.format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
      _options.end(_options.max());

      _tmpl.find(".start-date-custom").val(_options.min());
      _tmpl.find(".end-date-custom").val(_options.max());

      var _opts = [];
      // hide not useful options from interval
      if (_calculatedEndDate.diff(_calculatedStartDate, 'minutes') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'minutes') <= 60) {
        _opts = enableOptions("200MILLISECONDS", "1SECONDS", "1MINUTES", "5MINUTES", "10MINUTES", "30MINUTES");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'hours') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'hours') <= 12) {
        _opts = enableOptions("5MINUTES", "10MINUTES", "30MINUTES", "1HOURS", "3HOURS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'hours') > 12 && _calculatedEndDate.diff(_calculatedStartDate, 'hours') < 36) {
        _opts = enableOptions("10MINUTES", "30MINUTES", "1HOURS", "3HOURS", "12HOURS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 7) {
        _opts = enableOptions("30MINUTES", "1HOURS", "3HOURS", "12HOURS", "1DAYS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 7 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 14) {
        _opts = enableOptions("3HOURS", "12HOURS", "1DAYS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 14 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 31) {
        _opts = enableOptions("12HOURS", "1DAYS", "7DAYS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 1) {
        _opts = enableOptions("1DAYS", "7DAYS", "1MONTHS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 6) {
        _opts = enableOptions("1DAYS", "7DAYS", "1MONTHS", "6MONTHS");
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 12) {
        _opts = enableOptions("7DAYS", "1MONTHS", "6MONTHS", "1YEARS");
      }

      $(".interval-select").html(renderOptions(_opts));

      matchIntervals();
    }
  }
}


ko.bindingHandlers.augmenthtml = {
  render: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var _val = ko.unwrap(valueAccessor());
    var _enc = $("<span>").html(_val);
    if (_enc.find("style").length > 0) {
      var parser = new less.Parser();
      $(_enc.find("style")).each(function (cnt, item) {
        var _less = "#result-container {" + $(item).text() + "}";
        try {
          parser.parse(_less, function (err, tree) {
            $(item).text(tree.toCSS());
          });
        }
        catch (e) {
        }
      });
      $(element).html(_enc.html());
    }
    else {
      $(element).html(_val);
    }
  },
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
  }
}

ko.bindingHandlers.clearable = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var _el = $(element);

    function tog(v) {
      return v ? "addClass" : "removeClass";
    }

    _el.addClass("clearable");
    _el.on("input", function () {
      _el[tog(this.value)]("x");
      valueAccessor()(_el.val());
    }).on("mousemove", function (e) {
      _el[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)]("onX");
    }).on("click", function (e) {
      if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
        _el.removeClass("x onX").val("");
        valueAccessor()("");
      }
    });
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    $(element).val(ko.unwrap(valueAccessor()));
  }
}

ko.bindingHandlers.spinedit = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    $(element).spinedit({
      minimum: 0,
      maximum: 10000,
      step: 5,
      value: ko.unwrap(valueAccessor()),
      numberOfDecimals: 0
    });
    $(element).on("valueChanged", function (e) {
      valueAccessor()(e.value);
    });
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    $(element).spinedit("setValue", ko.unwrap(valueAccessor()));
  }
}

ko.bindingHandlers.codemirror = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var options = $.extend(valueAccessor(), {});
    var editor = CodeMirror.fromTextArea(element, options);
    element.editor = editor;
    editor.setValue(options.data());
    editor.refresh();
    var wrapperElement = $(editor.getWrapperElement());

    $(document).on("refreshCodemirror", function () {
      editor.setSize("100%", 300);
      editor.refresh();
    });

    $(document).on("addFieldToSource", function (e, field) {
      if ($(element).data("template")) {
        editor.replaceSelection("{{" + field.name() + "}}");
      }
    });

    $(document).on("addFunctionToSource", function (e, fn) {
      if ($(element).data("template")) {
        editor.replaceSelection(fn);
      }
    });

    $(".chosen-select").chosen({
      disable_search_threshold: 10,
      width: "75%"
    });
    $('.chosen-select').trigger('chosen:updated');

    var sourceDelay = -1;
    editor.on("change", function (cm) {
      clearTimeout(sourceDelay);
      var _cm = cm;
      sourceDelay = setTimeout(function () {
        valueAccessor().data(_cm.getValue());
        if ($(".widget-html-pill").parent().hasClass("active")) {
          $("[contenteditable=true]").html(stripHtmlFromFunctions(valueAccessor().data()));
        }
      }, 100);
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
      wrapperElement.remove();
    });
  },
  update: function (element, valueAccessor, allBindingsAccessor) {
    var editor = element.editor;
    editor.refresh();
  }
};