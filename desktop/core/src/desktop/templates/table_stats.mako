## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from desktop import conf
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="tableStats()">
<<<<<<< HEAD
=======

  <style>
    .more-link:focus,
    .more-link:hover {
      background-color: #FFF !important;
      border-top: 1px solid transparent !important;
      border-right: 1px solid transparent !important;
      border-left: 1px solid transparent !important;
    }
  </style>

>>>>>>> upstream/master
  <script type="text/html" id="table-stats">
    <div class="content">
      <!-- ko if: statRows().length -->
      <table class="table table-striped">
        <tbody data-bind="foreach: statRows">
          <tr><th data-bind="text: data_type, style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></th><td data-bind="text: comment, style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></td></tr>
        </tbody>
      </table>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="column-stats">
    <div class="pull-right filter" data-bind="visible: termsTabActive" style="display:none;">
      <input type="text" data-bind="textInput: prefixFilter" placeholder="${ _('Prefix filter...') }"/>
    </div>
    <div class="tab-content" style="border: none; margin-top: 10px">
      <div class="tab-pane active" id="columnAnalysisStats" style="text-align: left">
        <div class="alert" data-bind="visible: isComplexType" style="margin: 5px">${ _('Column stats are currently not supported for columns of type:') } <span data-bind="text: type"></span></div>
        <div class="content" data-bind="ifnot: isComplexType">
          <table class="table table-condensed">
            <tbody data-bind="foreach: statRows">
              <tr><th data-bind="text: Object.keys($data)[0], style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></th><td data-bind="text: $data[Object.keys($data)[0]], style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="tab-pane" id="columnAnalysisTerms" style="text-align: left">
        <i style="margin: 5px;" data-bind="visible: loadingTerms" class='fa fa-spinner fa-spin'></i>
        <div class="alert" data-bind="visible: ! loadingTerms() && terms().length == 0">${ _('There are no terms to be shown') }</div>
        <div class="content">
          <table class="table table-striped" data-bind="visible: ! loadingTerms()">
            <tbody data-bind="foreach: terms">
              <tr><td data-bind="text: name"></td><td style="width: 40px"><div class="progress"><div class="bar-label" data-bind="text: count"></div><div class="bar bar-info" style="margin-top: -20px;" data-bind="style: { 'width' : percent + '%' }"></div></div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="stats-popover">
<<<<<<< HEAD
    <div style="position: fixed; display: none;" class="popover show mega-popover right" data-bind="style: { 'top': popoverTop() + 'px', 'left': popoverLeft() + 'px' }, visible: analysisStats, with: analysisStats">
      <div class="arrow" data-bind="style: { 'top': $parent.popoverArrowTop() + 'px'}"></div>
      <h3 class="popover-title" style="text-align: left">
        <a class="pull-right pointer close-popover" style="margin-left: 8px" data-bind="click: $parent.toggleStats"><i class="fa fa-times"></i></a>
        <a class="pull-right pointer stats-refresh" style="margin-left: 8px" data-bind="visible: !isComplexType && !isView, click: refresh"><i class="fa fa-refresh" data-bind="css: { 'fa-spin' : refreshing }"></i></a>
        <span class="pull-right stats-warning muted" data-bind="visible: inaccurate() && column == null && !isComplexType && !isView" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }" style="margin-left: 8px"><i class="fa fa-exclamation-triangle"></i></span>
        <i data-bind="visible: loading" class='fa fa-spinner fa-spin'></i>
        <!-- ko if: column == null -->
        <strong class="table-name" data-bind="text: table"></strong> ${ _(' table analysis') }
        <!-- /ko -->
        <!-- ko ifnot: column == null -->
        <strong class="table-name" data-bind="text: column"></strong> ${ _(' column analysis') }
        <!-- /ko -->
      </h3>
      <div class="popover-content">
        <div class="alert" style="text-align: left; display:none" data-bind="visible: hasError">${ _('There is no analysis available') }</div>
        <!-- ko if: isComplexType && sourceType == 'impala' -->
        <div class="alert" style="text-align: left">${ _('Column analysis is currently not supported for columns of type:') } <span data-bind="text: type"></span></div>
        <!-- /ko -->
        <!-- ko template: {if: column == null && ! hasError() && ! (isComplexType && sourceType == 'impala'), name: 'table-stats' } --><!-- /ko -->
        <!-- ko template: {if: column != null && ! hasError() && ! (isComplexType && sourceType == 'impala'), name: 'column-stats' } --><!-- /ko -->
=======
    <div style="position: fixed; display: none; z-index: 5000;" class="popover show mega-popover right" data-bind="style: { 'top': popoverTop() + 'px', 'left': popoverLeft() + 'px' }, visible: analysisStats, with: analysisStats">
      <div class="arrow" data-bind="style: { 'top': $parent.popoverArrowTop() + 'px'}"></div>
      <h3 class="popover-title" style="text-align: left">
        <a class="pull-right pointer close-popover" style="margin-left: 8px" data-bind="click: $parent.toggleStats"><i class="fa fa-times"></i></a>
        <a class="pull-right pointer stats-refresh" style="margin-left: 8px" data-bind="visible: !isComplexType && !isView, click: refresh"><i class="fa fa-refresh" data-bind="css: { 'fa-spin' : refreshing }"></i></a> <i data-bind="visible: loadingStats" class='fa fa-spinner fa-spin'></i>
        <!-- ko if: column == null -->
        <strong class="table-name" data-bind="text: table"></strong> ${ _(' table') }
        <!-- /ko -->
        <!-- ko ifnot: column == null -->
        <strong class="table-name" data-bind="text: column"></strong> ${ _(' column') }
        <!-- /ko -->
      </h3>
      <div class="popover-content">
        <ul class="nav nav-tabs">
          <li class="active" data-bind="click: function () { activeTab('sample'); }, visible: column === null">
            <a class="inactive-action" href="#sampleTab" data-toggle="tab">${_('Sample')}</a>
          </li>
          <li data-bind="click: function () { activeTab('analysis'); }">
            <a class="inactive-action" href="#analysisTab" data-toggle="tab">${_('Analysis')} <span class="pull-right stats-warning muted" data-bind="visible: inaccurate() && column == null && !isComplexType && !isView" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }" style="margin-left: 8px"><i class="fa fa-exclamation-triangle"></i></span></a>
          </li>
          <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
          <li class="pull-right">
            <a class="more-link" target="_blank" data-bind="attr: { 'href': '/metastore/table/' + database + '/' + table }">
              <i class="fa fa-external-link" ></i> ${ _('View more...') }
            </a>
          </li>
          <!-- /ko -->
        </ul>
        <div class="tab-content" style="border: none">
          <div class="tab-pane active" id="sampleTab">
            <!-- ko hueSpinner: { spin: loadingSamples, center: true, size: 'large' } --><!-- /ko -->
            <!-- ko ifnot: loadingSamples -->
            <div style="max-height: 320px; overflow: auto; text-align: left; padding: 3px;">
              <!-- ko with: samples -->
              <!-- ko if: rows.length == 0 -->
              <div class="alert">${ _('The selected table has no data.') }</div>
              <!-- /ko -->
              <!-- ko if: rows.length > 0 -->
              <table class="table table-striped table-condensed">
                <tr>
                  <th style="width: 10px"></th>
                  <!-- ko foreach: headers -->
                  <th data-bind="text: $data"></th>
                  <!-- /ko -->
                </tr>
                <tbody>
                <!-- ko foreach: rows -->
                <tr>
                  <td data-bind="text: $index()+1"></td>
                  <!-- ko foreach: $data -->
                  <td style="white-space: pre;" data-bind="text: $data"></td>
                  <!-- /ko -->
                </tr>
                <!-- /ko -->
                </tbody>
              </table>
              <!-- /ko -->
              <!-- /ko -->
            </div>
            <!-- /ko -->
          </div>
          <div class="tab-pane" id="analysisTab">
            <!-- ko hueSpinner: { spin: loadingStats, center: true, size: 'large' } --><!-- /ko -->
            <!-- ko ifnot: loadingStats -->
            <div class="alert" style="text-align: left; display:none" data-bind="visible: statsHasError">${ _('There is no analysis available') }</div>
            <!-- ko if: isComplexType && sourceType == 'impala' -->
            <div class="alert" style="text-align: left">${ _('Column analysis is currently not supported for columns of type:') } <span data-bind="text: type"></span></div>
            <!-- /ko -->
            <!-- ko template: {if: column == null && ! statsHasError() && ! (isComplexType && sourceType == 'impala'), name: 'table-stats' } --><!-- /ko -->
            <!-- ko template: {if: column != null && ! statsHasError() && ! (isComplexType && sourceType == 'impala'), name: 'column-stats' } --><!-- /ko -->
            <!-- /ko -->
          </div>
        </div>
>>>>>>> upstream/master
      </div>
    </div>
  </script>

  <script type="text/html" id="table-stats-link">
<<<<<<< HEAD
    <a class="inactive-action" href="javascript:void(0)" data-bind="visible: enabled, click: toggleStats, css: { 'blue': analysisStats() || alwaysActive }"><i class='fa fa-bar-chart' title="${_('View statistics') }"></i></a>
    <!-- ko template: { if: analysisStats, name: 'stats-popover'} --><!-- /ko -->
=======
    <a class="inactive-action" href="javascript:void(0)" data-bind="visible: enabled, click: toggleStats, css: { 'blue': analysisStats() || alwaysActive }, "><i class='fa fa-bar-chart' title="${_('View statistics') }"></i></a>
>>>>>>> upstream/master
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        define("tableStats", ['knockout', 'desktop/js/assist/tableStats'], factory);
      } else {
        factory(ko, TableStats);
      }
    }(function (ko, TableStats) {

      function TableStatsViewModel(params, element) {
        var self = this;
        self.params = params;
        var $targetElement = $(element);
<<<<<<< HEAD
=======
        var $statsContainer = $('<div>').appendTo($('body'));

>>>>>>> upstream/master
        self.i18n = {
          errorLoadingStats: "${ _('There was a problem loading the stats.') }",
          errorRefreshingStats: "${ _('There was a problem refreshing the stats.') }",
          errorLoadingTerms: "${ _('There was a problem loading the terms.') }"
        };

        self.enabled = params.tableName || params.columnName;
        self.alwaysActive = params.alwaysActive || false;
        self.analysisStats = ko.observable(null);

        if (ko.isObservable(self.params.statsVisible)) {
          self.analysisStats.subscribe(function (newValue) {
            self.params.statsVisible(newValue !== null);
          })
        }

        self.popoverTop = ko.observable(0);
        self.popoverArrowTop = ko.observable(0);
        self.popoverLeft = ko.observable(0);

        var lastOffset = { top: -1, left: -1 };
        self.refreshPopoverPosition = function () {
<<<<<<< HEAD
          var $popover = $targetElement.find(".popover");
=======
          var $popover = $statsContainer.find(".popover");
>>>>>>> upstream/master
          if ($targetElement.is(":visible")) {
            var newTop = $targetElement.offset().top - $(window).scrollTop();
            if (lastOffset.left != $targetElement.offset().left || lastOffset.top != newTop) {
              lastOffset.left = $targetElement.offset().left + $targetElement.outerWidth();
              if ($popover.length) {
                lastOffset.top = newTop - ($popover.outerHeight() / 2) + ($targetElement.outerHeight() / 2)
              } else {
                lastOffset.top = newTop - 210;
              }
              self.popoverArrowTop($popover.outerHeight() / 2 + (lastOffset.top < 0 ? lastOffset.top - 10 : 0));

              lastOffset.top = Math.max(lastOffset.top, 10);
              self.popoverTop(lastOffset.top);
              self.popoverLeft(lastOffset.left);
              if (self.popoverArrowTop() < 80) {
                $popover.hide();
              } else {
                $popover.show();
              }
            }
          } else {
            $popover.hide();
          }
        }

        if (self.enabled) {
          window.setInterval(function () {
            if (self.analysisStats() == null) {
              return;
            }

            self.refreshPopoverPosition();
          }, 200);
        }

        self.analysisStats.subscribe(function (newValue) {
          if (newValue) {
            self.refreshPopoverPosition();
          }
        });

<<<<<<< HEAD
        $(document).click(function(event) {
          if(!$(event.target).closest($targetElement).length) {
            self.analysisStats(null)
          }
        })

        self.toggleStats = function (data, event) {
=======
        self.toggleStats = function (data, event) {
          $statsContainer.empty();
>>>>>>> upstream/master
          if (self.analysisStats()) {
            self.analysisStats(null);
          } else {
            self.analysisStats(new TableStats({
              i18n: self.i18n,
              sourceType: self.params.sourceType,
              databaseName: self.params.databaseName,
              tableName: self.params.tableName,
              columnName: self.params.columnName,
              assistHelper: self.params.assistHelper,
              type: self.params.fieldType
            }));
<<<<<<< HEAD
          }
        };
      }
=======

            var $popover = $('<div>');
            $statsContainer.append($popover)

            ko.renderTemplate('stats-popover', self, {
              afterRender: function(renderedElement) {
                var hideWhenClickOutside = function (event) {
                  if(!$(event.target).closest($statsContainer).length) {
                    self.analysisStats(null)
                    $(document).off('click', hideWhenClickOutside);
                  }
                }

                window.setTimeout(function () {
                  $(document).on('click', hideWhenClickOutside);
                }, 0)
              }
            }, $popover[0]);
          }
        };
      }

>>>>>>> upstream/master
      ko.components.register('table-stats', {
        viewModel: {
          createViewModel: function(params, componentInfo) {
            return new TableStatsViewModel(params, componentInfo.element);
          }
        },
        template: { element: 'table-stats-link' }
      });
    }));
  </script>
</%def>