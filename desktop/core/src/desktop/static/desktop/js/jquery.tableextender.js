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
      fixedHeader: false,
      fixedFirstColumn: false,
      fixedFirstColumnTopMargin: 0,
      headerSorting: true,
      lockSelectedRow: false,
      firstColumnTooltip: false,
      classToRemove: 'resultTable',
      hintElement: null,
      includeNavigator: true,
      mainScrollable: window,
      stickToTopPosition: -1,
      labels: {
        GO_TO_COLUMN: "Go to column:",
        PLACEHOLDER: "column name...",
        LOCK: "Click to lock row",
        UNLOCK: "Click to unlock row"
      }
    };

  function Plugin(element, options) {
    var self = this;
    self.element = element;
    self.setOptions(options);
    self._name = pluginName;
    self.init();
  }

  Plugin.prototype.setOptions = function (options) {
    if (typeof jHueTableExtenderGlobals != 'undefined') {
      var extendedDefaults = $.extend({}, defaults, jHueTableExtenderGlobals);
      extendedDefaults.labels = $.extend({}, defaults.labels, jHueTableExtenderGlobals.labels);
      this.options = $.extend({}, extendedDefaults, options);
      if (options != null) {
        this.options.labels = $.extend({}, extendedDefaults.labels, options.labels);
      }
    } else {
      this.options = $.extend({}, defaults, options);
      if (options != null) {
        this.options.labels = $.extend({}, defaults.labels, options.labels);
      }
    }

    this._defaults = defaults;

    if (this.options.fixedHeader) {
      drawHeader(this);
    }
    if (this.options.fixedFirstColumn) {
      drawFirstColumn(this);
    }
  };

  Plugin.prototype.resetSource = function () {
    var _this = this;
    if (_this.options.includeNavigator) {
      var source = [];
      $(this.element).find("th").each(function () {
        source.push($(this).text());
      });

      $("#jHueTableExtenderNavigator").find("input").data('typeahead').source = source;
    }
  };

  Plugin.prototype.drawHeader = function (skipCreation) {
    drawHeader(this, skipCreation);
  };

  Plugin.prototype.drawFirstColumn = function () {
    drawFirstColumn(this);
  };

  Plugin.prototype.drawLockedRows = function (force) {
    var _this = this;
    var $pluginElement = $(_this.element);
    if ($pluginElement.data('lockedRows')) {
      var locks = $pluginElement.data('lockedRows');
      Object.keys(locks).forEach(function (idx) {
        drawLockedRow(_this, idx.substr(1), force);
      });
    }
  };

  Plugin.prototype.init = function () {
    var self = this;

    $.expr[":"].econtains = function (obj, index, meta, stack) {
      return (obj.textContent || obj.innerText || $(obj).text() || "").toLowerCase() == meta[3].toLowerCase();
    };

    var $element = $(self.element);

    if (self.options.includeNavigator) {
      var jHueTableExtenderNavigator = $("<div>").attr("id", "jHueTableExtenderNavigator");
      $("<a>").attr("href", "#").addClass("pull-right").html("&times;").click(function (e) {
        e.preventDefault();
        $(this).parent().hide();
      }).appendTo(jHueTableExtenderNavigator);
      $("<label>").html(self.options.labels.GO_TO_COLUMN + " <input type=\"text\" placeholder=\"" + self.options.labels.PLACEHOLDER + "\" />").appendTo(jHueTableExtenderNavigator);

      jHueTableExtenderNavigator.appendTo($("body"));

      $element.find("tbody").click(function (event) {
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
      $element.find("th").each(function () {
        source.push($(this).text());
      });

      jHueTableExtenderNavigator.find("input").typeahead({
        source: source,
        updater: function (item) {
          jHueTableExtenderNavigator.hide();
          $element.find("tr td:nth-child(" + ($(self.element).find("th:econtains(" + item + ")").index() + 1) + ")").addClass("columnSelected");
          if (self.options.firstColumnTooltip) {
            $element.find("tr td:nth-child(" + ($(self.element).find("th:econtains(" + item + ")").index() + 1) + ")").each(function () {
              $(this).attr("rel", "tooltip").attr("title", "#" + $(this).parent().find("td:first-child").text()).tooltip({
                placement: 'left'
              });
            });
          }
          $(self.element).parent().animate({
            scrollLeft: $(self.element).find("th:econtains(" + item + ")").position().left + $(self.element).parent().scrollLeft() - $(self.element).parent().offset().left - 30
          }, 300);
          $(self.element).find("tr.rowSelected td:nth-child(" + ($(self.element).find("th:econtains(" + item + ")").index() + 1) + ")").addClass("cellSelected");
        }
      });

      $element.parent().bind("mouseleave", function () {
        jHueTableExtenderNavigator.hide();
      });

      jHueTableExtenderNavigator.bind("mouseenter", function (e) {
        jHueTableExtenderNavigator.show();
      });
    }

    if (self.options.hintElement != null) {
      var $hintElement = $(self.options.hintElement);
      var showAlertTimeout = -1;
      $element.find("tbody").mousemove(function () {
        window.clearTimeout(showAlertTimeout);
        if ($hintElement.data("show") == null || $hintElement.data("show")) {
          showAlertTimeout = window.setTimeout(function () {
            $hintElement.fadeIn();
          }, 1300);
        }
      });

      $hintElement.find(".close").click(function () {
        $hintElement.data("show", false);
      });
    }

    if (self.options.fixedHeader) {
      drawHeader(self);
    }
    if (self.options.fixedFirstColumn) {
      drawFirstColumn(self);
    }

    $(document).on('click dblclick', '.dataTables_wrapper > table tbody tr', function () {
      $('.dataTables_wrapper > .jHueTableExtenderClonedContainerColumn table tbody tr.selected').removeClass('selected');
      if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
      } else {
        $('.dataTables_wrapper > table tbody tr.selected').removeClass('selected');
        $(this).addClass('selected');
        $('.dataTables_wrapper > .jHueTableExtenderClonedContainerColumn table tbody tr:eq('+($(this).index())+')').addClass('selected');
      }
    });

    $(document).on('dblclick', '.dataTables_wrapper > table tbody tr', function () {
      if (huePubSub){
        huePubSub.publish('table.row.dblclick', {idx: $(this).index(), table: $(this).parents('table')});
      }
    });

    var $pluginElement = $(self.element);
    $pluginElement.parent().resize(function () {
      $pluginElement.data('clonedTableContainer').height($pluginElement.parent().get(0).scrollHeight);
      $pluginElement.data('clonedTableVisibleContainer').height($pluginElement.parent().height());
    });

    var scrollThrottle = -1;
    var lastMarginTop = -$pluginElement.parent().scrollTop() + self.options.fixedFirstColumnTopMargin;
    var newMarginTop;
    $pluginElement.parent().scroll(function () {
      window.clearTimeout(scrollThrottle);
      scrollThrottle = window.setTimeout(function () {
        newMarginTop = -$pluginElement.parent().scrollTop() + self.options.fixedFirstColumnTopMargin;
        if (newMarginTop !== lastMarginTop) {
          $pluginElement.data('clonedTableContainer').css("marginTop", newMarginTop + "px");
          lastMarginTop = newMarginTop;
        }
      }, 50);
    });
    $pluginElement.data('clonedTableContainer').css("marginTop", lastMarginTop + "px");

    var topPos, pos;
    var $parent = $pluginElement.parent();
    function positionClones() {
      pos = self.options.stickToTopPosition;
      if (typeof pos === 'function'){
        pos = pos();
      }
      if (pos > -1) {
        topPos = $pluginElement.offset().top;
        if (topPos < pos) {
          $pluginElement.data('clonedCellVisibleContainer').css("top", pos + "px");
        } else {
          $pluginElement.data('clonedCellVisibleContainer').css("top", topPos + "px");
        }
        $pluginElement.data('clonedTableVisibleContainer').css("top", topPos + "px");
      } else {
        if (self.options.clonedContainerPosition == 'absolute') {
          topPos = $parent.position().top;
        } else {
          topPos = $parent.offset().top;
        }
        $pluginElement.data('clonedTableVisibleContainer').css("top", topPos + "px");
        $pluginElement.data('clonedCellVisibleContainer').css("top", topPos + "px");
      }
    }

    positionClones();

    var $mainScrollable = $(self.options.mainScrollable);
    if ($mainScrollable.data('lastScroll')) {
      $mainScrollable.off('scroll', $mainScrollable.data('lastScroll'));
      $mainScrollable.data('lastScroll', false);
    }
    if (navigator.userAgent.toLowerCase().indexOf("firefox") > 0) {
      var ffThrottle = -1;
      var throttledPositionClones = function () {
        window.clearTimeout(ffThrottle);
        ffThrottle = window.setTimeout(positionClones, 10);
      };
      $mainScrollable.on('scroll', throttledPositionClones);
      $mainScrollable.data('lastScroll', throttledPositionClones);
    } else {
      $mainScrollable.on('scroll', positionClones);
      $mainScrollable.data('lastScroll', positionClones);
    }
  };

  function drawLockedRow(plugin, rowNo, force) {
    var $pluginElement = $(plugin.element);
    var lockedRows = $pluginElement.data('lockedRows') || {};
    var $header = $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainer");
    var $headerCounter = $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainerCell");
    $header.addClass('locked');
    $headerCounter.addClass('locked');

    function unlock($el) {
      $header.find('tr td:first-child').filter(function () {
        return $(this).text() === rowNo + '';
      }).closest('tr').remove();
      delete lockedRows['r' + $el.text()];
      $el.parent().remove();
      if ($header.find('tbody tr').length == 0) {
        $header.removeClass('locked');
        $headerCounter.removeClass('locked');
      }
    }

    if (Object.keys(lockedRows).indexOf('r' + rowNo) === -1 || force) {
      if (force) {
        unlock(lockedRows['r' + rowNo].cell.find('td'));
      }
      var $clone = $('<tr>');
      var tHtml = '';
      var aoColumns = $pluginElement.data('aoColumns');
      $pluginElement.data('data')[rowNo - 1].forEach(function(col, idx){
        tHtml += '<td ' + (aoColumns && !aoColumns[idx].bVisible ? 'style="display: none"' : '') + '>' + col + '</td>';
      });
      $clone.html(tHtml);
      $clone.addClass('locked');
      $clone.appendTo($header.find('tbody'));
      $pluginElement.data('lockedRows', lockedRows);
      var $newTr = $('<tr>');
      $newTr.addClass('locked').html('<td class="pointer unlockable" title="' + plugin.options.labels.UNLOCK + '"><i class="fa fa-unlock muted"></i>' + rowNo + '</td>').appendTo($headerCounter.find('tbody'));
      $newTr.find('td').on('click', function () {
        unlock($(this));
      });
      lockedRows['r' + rowNo] = {
        row: $clone,
        cell: $newTr
      };
    } else {
      lockedRows['r' + rowNo].row.appendTo($header.find('tbody'));
      lockedRows['r' + rowNo].cell.appendTo($headerCounter.find('tbody'));
      lockedRows['r' + rowNo].cell.find('td').on('click', function () {
        unlock($(this));
      });
    }
  }

  function drawFirstColumn(plugin) {
    var $pluginElement = $(plugin.element);
    if (!$pluginElement.attr("id") && plugin.options.parentId) {
      $pluginElement.attr("id", "eT" + plugin.options.parentId);
    }

    var mainScrollable = plugin.options.mainScrollable;
    var originalTh = $(plugin.element).find("thead>tr th:eq(0)");
    var topPosition;
    if (plugin.options.clonedContainerPosition == 'absolute') {
      topPosition = $pluginElement.parent().position().top - $(mainScrollable).scrollTop();
    } else {
      topPosition = $pluginElement.parent().offset().top - $(mainScrollable).scrollTop();
    }

    $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainerCell").remove();
    var clonedCell = $('<table>').attr('class', $(plugin.element).attr('class'));
    clonedCell.removeClass(plugin.options.classToRemove);
    clonedCell.css("margin-bottom", "0").css("table-layout", "fixed");
    var clonedCellTHead = $('<thead>');
    clonedCellTHead.appendTo(clonedCell);
    var clonedCellTH = originalTh.clone();
    clonedCellTH.appendTo(clonedCellTHead);
    clonedCellTH.width(originalTh.width()).css({
      "background-color": "#FFFFFF",
      "border-color": "transparent"
    });
    clonedCellTH.click(function () {
      originalTh.click();
    });
    $('<tbody>').appendTo(clonedCell);

    var clonedCellContainer = $("<div>").css("background-color", "#FFFFFF").width(originalTh.outerWidth());

    clonedCell.appendTo(clonedCellContainer);

    var clonedCellVisibleContainer = $("<div>").attr("id", $(plugin.element).attr("id") + "jHueTableExtenderClonedContainerCell").addClass("jHueTableExtenderClonedContainerCell").width(originalTh.outerWidth()).css("overflow", "hidden").css("top", topPosition + "px");
    clonedCellVisibleContainer.css("position", plugin.options.clonedContainerPosition || "fixed");

    clonedCellContainer.appendTo(clonedCellVisibleContainer);

    $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainerColumn").remove();
    var clonedTable = $('<table>').attr('class', $(plugin.element).attr('class')).html('<thead></thead><tbody></tbody>');
    clonedTable.removeClass(plugin.options.classToRemove);
    clonedTable.css("margin-bottom", "0").css("table-layout", "fixed");
    $(plugin.element).find("thead>tr th:eq(0)").clone().appendTo(clonedTable.find('thead'));
    var clonedTBody = clonedTable.find('tbody');
    var clones = $(plugin.element).find("tbody>tr td:nth-child(1)").clone();
    var h = '';
    clones.each(function(){
      h+= '<tr><td>' + $(this).html() +'</td></tr>';
    });
    clonedTBody.html(h);
    if (plugin.options.lockSelectedRow) {
      clonedTBody.find('td').each(function(){
        var cell = $(this);
        cell.attr('title', plugin.options.labels.LOCK).addClass('lockable pointer').on('click', function(){
          drawLockedRow(plugin, $(this).text()*1);
        });
        $('<i>').addClass('fa fa-lock muted').prependTo(cell);
      });
    }
    clonedTable.find("thead>tr th:eq(0)").width(originalTh.width()).css("background-color", "#FFFFFF");

    var clonedTableContainer = $("<div>").css("background-color", "#FFFFFF").width(originalTh.outerWidth()).height($pluginElement.parent().get(0).scrollHeight);
    clonedTable.appendTo(clonedTableContainer);

    var clonedTableVisibleContainer = $("<div>").attr("id", $pluginElement.attr("id") + "jHueTableExtenderClonedContainerColumn").addClass("jHueTableExtenderClonedContainerColumn").width(originalTh.outerWidth()).height($pluginElement.parent().height()).css("overflow", "hidden").css("top", topPosition + "px");
    clonedTableVisibleContainer.css("position", plugin.options.clonedContainerPosition || "fixed");

    clonedTableContainer.appendTo(clonedTableVisibleContainer);
    clonedTableVisibleContainer.appendTo($pluginElement.parent());

    clonedCellVisibleContainer.appendTo($pluginElement.parent());

    $pluginElement.data('clonedTableContainer', clonedTableContainer);
    $pluginElement.data('clonedCellVisibleContainer', clonedCellVisibleContainer);
    $pluginElement.data('clonedTableVisibleContainer', clonedTableVisibleContainer);

    window.clearInterval($pluginElement.data('firstcol_interval'));
    var firstColInt = window.setInterval(function () {
      if ($pluginElement.parent().height() != $pluginElement.parent().data("h")) {
        clonedTableContainer.height($pluginElement.parent().get(0).scrollHeight);
        clonedTableVisibleContainer.height($pluginElement.parent().height());
        $pluginElement.parent().data("h", clonedTableVisibleContainer.height());
      }
    }, 250);
    $pluginElement.data('firstcol_interval', firstColInt);
  }

  function drawHeader(plugin, skipCreation) {
    var $pluginElement = $(plugin.element);

    if (! $pluginElement.is(':visible')) {
      if (typeof $pluginElement.data('updateThWidthsInterval') !== 'undefined') {
        window.clearInterval($pluginElement.data('updateThWidthsInterval'));
      }
      return;
    }

    if (!$pluginElement.attr("id") && plugin.options.parentId) {
      $pluginElement.attr("id", "eT" + plugin.options.parentId);
    }

    if (typeof skipCreation === 'undefined') {
      var mainScrollable = plugin.options.mainScrollable;

      $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainer").remove();
      var clonedTable = $('<table>').attr('class', $(plugin.element).attr('class'));
      clonedTable.removeClass(plugin.options.classToRemove);
      clonedTable.css("margin-bottom", "0").css("table-layout", "fixed");
      var clonedTableTHead = $('<thead>');
      clonedTableTHead.appendTo(clonedTable);
      var clonedTableTR = $pluginElement.find('thead>tr').clone();
      clonedTableTR.appendTo(clonedTableTHead);
      $('<tbody>').appendTo(clonedTable);

      var clonedThs = clonedTable.find("thead>tr th");
      clonedThs.wrapInner('<span></span>');

      if (typeof $pluginElement.data('updateThWidthsInterval') !== 'undefined') {
        window.clearInterval($pluginElement.data('updateThWidthsInterval'));
      }

      var thMapping = [];
      $pluginElement.find("thead>tr th").each(function (i) {
        var originalTh = $(this);
        originalTh.removeAttr("data-bind");
        var clonedTh = $(clonedThs[i]).css("background-color", "#FFFFFF").click(function () {
          originalTh.click();
          if (plugin.options.headerSorting) {
            clonedThs.attr("class", "sorting");
          }
          $(this).attr("class", originalTh.attr("class"));
        });
        thMapping.push({
          original: originalTh,
          clone: clonedTh
        })
      });
      $pluginElement.data('thMapping', thMapping);

      var clonedTableContainer = $("<div>").width($pluginElement.outerWidth());
      clonedTable.appendTo(clonedTableContainer);

      var topPosition;
      if (plugin.options.clonedContainerPosition == 'absolute') {
        topPosition = $pluginElement.parent().position().top - $(mainScrollable).scrollTop();
      } else {
        topPosition = $pluginElement.parent().offset().top - $(mainScrollable).scrollTop();
      }
      var clonedTableVisibleContainer = $("<div>").attr("id", $pluginElement.attr("id") + "jHueTableExtenderClonedContainer").addClass("jHueTableExtenderClonedContainer").width($pluginElement.parent().width()).css("overflow-x", "hidden").css("top", topPosition + "px");
      clonedTableVisibleContainer.css("position", plugin.options.clonedContainerPosition || "fixed");

      clonedTableContainer.appendTo(clonedTableVisibleContainer);
      clonedTableVisibleContainer.prependTo($pluginElement.parent());

      var updateThWidths = function () {
        clonedTableVisibleContainer.width($pluginElement.parent().width());
        $pluginElement.data('thMapping').forEach(function (mapping) {
          if (mapping.clone.width() !== mapping.original.width()) {
            mapping.clone.width(mapping.original.width())
          }
        });
      };

      updateThWidths();
      $pluginElement.data('updateThWidthsInterval', window.setInterval(updateThWidths, 300));

      function throttledHeaderPadding() {
        var firstCellWidth = clonedTable.find("thead>tr th:eq(0)").outerWidth();
        clonedTable.find("thead>tr th").each(function () {
          var leftPosition = $(this).position().left - firstCellWidth;
          if (leftPosition + $(this).outerWidth() > 0 && leftPosition < 0) {
            if ($(this).find('span').width() + -leftPosition < $(this).outerWidth() - 20) { // 20 is the sorting css width
              $(this).find('span').css('paddingLeft', -leftPosition);
            }
          } else {
            $(this).find('span').css('paddingLeft', 0);
          }
        });
      }

      var scrollTimeout = -1;
      $pluginElement.parent().scroll(function () {
        var scrollLeft = $(this).scrollLeft();
        clonedTableVisibleContainer.scrollLeft(scrollLeft);
        window.clearTimeout(scrollTimeout);
        scrollTimeout = window.setTimeout(throttledHeaderPadding, 200);
      });

      $pluginElement.bind('headerpadding', function () {
        scrollTimeout = window.setTimeout(throttledHeaderPadding, 200);
      });

      clonedTableVisibleContainer.scrollLeft($pluginElement.parent().scrollLeft());

      $pluginElement.parent().resize(function () {
        clonedTableVisibleContainer.width($(this).width());
      });

      function positionClones() {
        var pos = plugin.options.stickToTopPosition;
        if (typeof pos === 'function') {
          pos = pos();
        }
        if (pos > -1) {
          if ($pluginElement.offset().top < pos) {
            clonedTableVisibleContainer.css("top", pos + "px");
          } else {
            clonedTableVisibleContainer.css("top", $pluginElement.offset().top + "px");
          }
        } else {
          if (plugin.options.clonedContainerPosition == 'absolute') {
            clonedTableVisibleContainer.css("top", ($pluginElement.parent().position().top) + "px");
          } else {
            clonedTableVisibleContainer.css("top", ($pluginElement.parent().offset().top) + "px");
          }
        }
      }

      positionClones();

      $(mainScrollable).on('scroll', positionClones);
    } else {
      $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainer").children('div').width($pluginElement.outerWidth());
      $pluginElement.find("thead>tr th").each(function (i) {
        var originalTh = $(this);
        $("#" + $pluginElement.attr("id") + "jHueTableExtenderClonedContainer").find("thead>tr th:eq(" + i + ")").width(originalTh.width()).attr('class', originalTh.attr('class'));
      });
    }
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
      } else {
        $.data(this, 'plugin_' + pluginName).resetSource();
        $.data(this, 'plugin_' + pluginName).setOptions(options);
      }
    });
  }

})(jQuery, window, document);
