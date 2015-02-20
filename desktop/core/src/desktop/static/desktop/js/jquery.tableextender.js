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
 * jHue table extender plugin
 *
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueTableExtender",
      defaults = {
        fixedHeader:false,
        firstColumnTooltip:false,
        hintElement:null,
        includeNavigator: true,
        labels:{
          GO_TO_COLUMN:"Go to column:",
          PLACEHOLDER:"column name..."
        }
      };

  function Plugin(element, options) {
    this.element = element;
    if (typeof jHueTableExtenderGlobals != 'undefined') {
      var extendedDefaults = $.extend({}, defaults, jHueFileChooserGlobals);
      extendedDefaults.labels = $.extend({}, defaults.labels, jHueFileChooserGlobals.labels);
      this.options = $.extend({}, extendedDefaults, options);
      if (options != null) {
        this.options.labels = $.extend({}, extendedDefaults.labels, options.labels);
      }
    }
    else {
      this.options = $.extend({}, defaults, options);
      if (options != null) {
        this.options.labels = $.extend({}, defaults.labels, options.labels);
      }
    }
    this._defaults = defaults;
    this._name = pluginName;
    this.previousPath = "";
    this.init();
  }

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
    drawHeader(this);
  };

  Plugin.prototype.resetSource = function() {
    var _this = this;
    if (_this.options.includeNavigator){
      var source = [];
      $(this.element).find("th").each(function () {
        source.push($(this).text());
      });

      $("#jHueTableExtenderNavigator").find("input").data('typeahead').source = source;
    }
  };

  Plugin.prototype.init = function () {

    $.expr[":"].econtains = function (obj, index, meta, stack) {
      return (obj.textContent || obj.innerText || $(obj).text() || "").toLowerCase() == meta[3].toLowerCase();
    }

    var _this = this;
    if (_this.options.includeNavigator){
      var jHueTableExtenderNavigator = $("<div>").attr("id", "jHueTableExtenderNavigator");
      $("<a>").attr("href", "#").addClass("pull-right").html("&times;").click(function (e) {
        e.preventDefault();
        $(this).parent().hide();
      }).appendTo(jHueTableExtenderNavigator);
      $("<label>").html(_this.options.labels.GO_TO_COLUMN + " <input type=\"text\" placeholder=\"" + _this.options.labels.PLACEHOLDER + "\" />").appendTo(jHueTableExtenderNavigator);

      jHueTableExtenderNavigator.appendTo($("body"));

      $(_this.element).find("tbody").click(function (event) {
        if ($.trim(getSelection()) == "") {
          window.setTimeout(function () {
            $(".rowSelected").removeClass("rowSelected");
            $(".columnSelected").removeClass("columnSelected");
            $(".cellSelected").removeClass("cellSelected");
            $(event.target.parentNode).addClass("rowSelected");
            $(event.target.parentNode).find("td").addClass("rowSelected");
            jHueTableExtenderNavigator
                .css("left", (event.pageX + jHueTableExtenderNavigator.width() > $(window).width() - 10 ? event.pageX - jHueTableExtenderNavigator.width() - 10 : event.pageX) + "px")
                .css("top", (event.pageY + 10) + "px").show();
            jHueTableExtenderNavigator.find("input").focus();
          }, 100);
        }
      });

      var source = [];
      $(_this.element).find("th").each(function () {
        source.push($(this).text());
      });

      jHueTableExtenderNavigator.find("input").typeahead({
        source:source,
        updater:function (item) {
          jHueTableExtenderNavigator.hide();
          $(_this.element).find("tr td:nth-child(" + ($(_this.element).find("th:econtains(" + item + ")").index() + 1) + ")").addClass("columnSelected");
          if (_this.options.firstColumnTooltip) {
            $(_this.element).find("tr td:nth-child(" + ($(_this.element).find("th:econtains(" + item + ")").index() + 1) + ")").each(function () {
              $(this).attr("rel", "tooltip").attr("title", "#" + $(this).parent().find("td:first-child").text()).tooltip({
                placement:'left'
              });
            });
          }
          $(_this.element).parent().animate({
            scrollLeft:$(_this.element).find("th:econtains(" + item + ")").position().left + $(_this.element).parent().scrollLeft() - $(_this.element).parent().offset().left - 30
          }, 300);
          $(_this.element).find("tr.rowSelected td:nth-child(" + ($(_this.element).find("th:econtains(" + item + ")").index() + 1) + ")").addClass("cellSelected");
        }
      });

      $(_this.element).parent().bind("mouseleave", function () {
        jHueTableExtenderNavigator.hide();
      });

      jHueTableExtenderNavigator.bind("mouseenter", function (e) {
        jHueTableExtenderNavigator.show();
      });
    }

    if (_this.options.hintElement != null) {
      var showAlertTimeout = -1;
      $(_this.element).find("tbody").mousemove(function () {
        window.clearTimeout(showAlertTimeout);
        if ($(_this.options.hintElement).data("show") == null || $(_this.options.hintElement).data("show")) {
          showAlertTimeout = window.setTimeout(function () {
            $(_this.options.hintElement).fadeIn();
          }, 1300);
        }
      });

      $(_this.options.hintElement).find(".close").click(function () {
        $(_this.options.hintElement).data("show", false);
      });
    }

    if (_this.options.fixedHeader) {
      drawHeader(_this);
    }

  };

  function s4() {
  return Math.floor((1 + Math.random()) * 0x10000)
        .toString(16)
        .substring(1);
  }


  function UUID() {
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
  }


  function drawHeader(plugin) {
    if (!$(plugin.element).attr("id") && plugin.options.parentId){
      $(plugin.element).attr("id", "eT" + plugin.options.parentId);
    }
    $("#" + $(plugin.element).attr("id") + "jHueTableExtenderClonedContainer").remove();
    var clonedTable = $(plugin.element).clone();
    clonedTable.css("margin-bottom", "0").css("table-layout", "fixed");
    clonedTable.removeAttr("id").removeClass("resultTable").find("tbody").remove();
    $(plugin.element).find("thead>tr th").each(function (i) {
      var originalTh = $(this);
      clonedTable.find("thead>tr th:eq(" + i + ")").width(originalTh.width()).css("background-color", "#FFFFFF");
      clonedTable.find("thead>tr th:eq(" + i + ")").click(function () {
        originalTh.click();
        clonedTable.find("thead>tr th").attr("class", "sorting");
        $(this).attr("class", originalTh.attr("class"));
      });
    });
    var clonedTableContainer = $("<div>").width($(plugin.element).outerWidth());
    clonedTable.appendTo(clonedTableContainer);

    var clonedTableVisibleContainer = $("<div>").attr("id", $(plugin.element).attr("id") + "jHueTableExtenderClonedContainer").addClass("jHueTableExtenderClonedContainer").width($(plugin.element).parent().width()).css("overflow-x", "hidden").css("top", ($(plugin.element).parent().offset().top - $(window).scrollTop()) + "px");
    clonedTableVisibleContainer.css("position", "fixed");

    clonedTableContainer.appendTo(clonedTableVisibleContainer);
    clonedTableVisibleContainer.prependTo($(plugin.element).parent());

    $(plugin.element).parent().scroll(function () {
      clonedTableVisibleContainer.scrollLeft($(this).scrollLeft());
    });

    $(plugin.element).parent().data("w", clonedTableVisibleContainer.width());

    window.setInterval(function () {
      if ($(plugin.element).parent().width() != $(plugin.element).parent().data("w")) {
        clonedTableVisibleContainer.width($(plugin.element).parent().width());
        $(plugin.element).parent().data("w", clonedTableVisibleContainer.width());
        $(plugin.element).find("thead>tr th").each(function (i) {
          clonedTable.find("thead>tr th:eq(" + i + ")").width($(this).width()).css("background-color", "#FFFFFF");
        });
      }
    }, 250);

    $(plugin.element).parent().resize(function () {
      clonedTableVisibleContainer.width($(this).width());
    });

    $(window).scroll(function () {
      clonedTableVisibleContainer.css("top", ($(plugin.element).parent().offset().top - $(window).scrollTop()) + "px");
    });
  }

  function getSelection() {
    var t = '';
    if (window.getSelection) {
      t = window.getSelection();
    } else if (document.getSelection) {
      t = document.getSelection();
    } else if (document.selection) {
      t = document.selection.createRange().text;
    }
    return t.toString();
  }

  $.fn[pluginName] = function (options) {
    return this.each(function () {
      if (!$.data(this, 'plugin_' + pluginName)) {
        $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
      }
      else {
        $.data(this, 'plugin_' + pluginName).resetSource();
        $.data(this, 'plugin_' + pluginName).setOptions(options);
      }
    });
  }

})(jQuery, window, document);
