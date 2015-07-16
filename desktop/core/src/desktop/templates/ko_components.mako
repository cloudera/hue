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
%>

<%def name="assistPanel()">
  <script type="text/html" id="assist-panel-template">
    <div class="assist-container" data-bind="visible: isAssistVisible() && isAssistAvailable(), css:{'span2': isAssistVisible(), 'hidden': !isAssistVisible() }">
      <div class="span2 assist">

        <a title="${_('Toggle Assist')}" class="pull-right pointer assist-action" data-bind="click: toggleAssist">
          <i class="fa fa-chevron-left"></i>
        </a>
        <a title="${_('Manually refresh the table list')}" rel="tooltip" data-placement="top" class="pull-right pointer assist-action" data-bind="click: reloadAssist">
          <i class="fa fa-refresh"></i>
        </a>
        <ul class="nav nav-list" style="border: none; padding: 0; background-color: #FFF; margin-bottom: 1px;">
          <li class="nav-header">${_('database')}</li>
        </ul>
        <!-- ko if: assist.mainObjects().length > 0 -->
        <select data-bind="options: assist.mainObjects, select2: { width: '100%', placeholder: '${ _("Choose a database...") }', update: assist.selectedMainObject}" class="input-medium" data-placeholder="${_('Choose a database...')}"></select>
        <input type="text" placeholder="${ _('Table name...') }" style="width:90%; margin-top: 20px" data-bind="value: assist.filter, valueUpdate: 'afterkeydown'"/>

        <div data-bind="visible: Object.keys(assist.firstLevelObjects()).length == 0">${_('The selected database has no tables.')}</div>
        <ul data-bind="visible: Object.keys(assist.firstLevelObjects()).length > 0, foreach: assist.filteredFirstLevelObjects()" class="unstyled assist-main">
          <li data-bind="event: { mouseover: function(){ $('#assistHover_' + $data).show(); }, mouseout: function(){ $('#assistHover_' + $data).hide(); } }">
            <a href="javascript:void(0)" data-bind="attr: {'id': 'assistHover_' + $data}, click: $parent.showTablePreview" style="display: none; position: absolute; right: 10px; margin-left: auto; background-color: #FFF" class="preview-sample"><i class="fa fa-list" title="${'Preview Sample data'}" style="margin-left:5px"></i></a>
            <a href="javascript:void(0)" data-bind="click: $parent.loadAssistSecondLevel, event: { 'dblclick': function(){ huePubSub.publish('assist.dblClickItem', $data); } }"><span data-bind="text: $data"></span></a>
            <div data-bind="visible: $parent.assist.firstLevelObjects()[$data].loaded() && $parent.assist.firstLevelObjects()[$data].open()">
              <ul data-bind="visible: $parent.assist.firstLevelObjects()[$data].items().length > 0, foreach: $parent.assist.firstLevelObjects()[$data].items()" class="unstyled">
                <li><a data-bind="attr: {'title': $parents[1].secondLevelTitle($data)}" style="padding-left:10px" href="javascript:void(0)"><span data-bind="html: $parents[1].truncateSecondLevel($data), event: { 'dblclick': function() { huePubSub.publish('assist.dblClickItem', $data.name +', '); } }"></span></a></li>
              </ul>
            </div>
          </li>
        </ul>
        <!-- /ko -->

        <div id="navigatorLoader" class="center"  data-bind="visible: assist.isLoading">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>

        <div class="center" data-bind="visible: assist.hasErrors">
          ${ _('The database list cannot be loaded.') }
        </div>
      </div>

      <div id="assistQuickLook" class="modal hide fade">
        <div class="modal-header">
          <a href="#" class="close" data-dismiss="modal">&times;</a>
          <h3>${_('Data sample for')} <span class="tableName"></span></h3>
        </div>
        <div class="modal-body" style="min-height: 100px">
          <div class="loader">
            <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
            <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
          </div>
          <div class="sample"></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Ok')}</button>
        </div>
      </div>

    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function() {
      function AssistPanel(params) {
        var self = this;

        self.assist = params.assist;

        self.isAssistVisible = params.isAssistVisible;
        self.isAssistAvailable = params.isAssistAvailable;

        self.isAssistVisible($.totalStorage(params.totalStorageId) != null && $.totalStorage(params.totalStorageId));

        self.isAssistVisible.subscribe(function(newValue) {
          $.totalStorage(params.totalStorageId, newValue);
        });

        self.toggleAssist = function () {
          self.isAssistVisible(!self.isAssistVisible());
        };

        self.modalItem = ko.observable();

        self.secondLevelTitle = function(level) {
          var _title = "";

          if (level.comment && needsTruncation(level)) {
            _title = level.name + " (" + level.type + "): " + level.comment;
          } else if (needsTruncation(level)) {
            _title = level.name + " (" + level.type + ")";
          } else if (level.comment) {
            _title = level.comment;
          }
          return _title;
        };

        var needsTruncation = function(level) {
          return (level.name.length + level.type.length) > 20;
        };

        self.truncateSecondLevel = function(level) {
          var escapeString = function (str) {
            return $("<span>").text(str).html().trim()
          };
          if (needsTruncation(level)) {
            return escapeString(level.name + " (" + level.type + ")").substr(0, 20) + "&hellip;";
          }
          return escapeString(level.name + " (" + level.type + ")");
        };

        function resizeAssist() {
          $(".assist").parents(".span2").height($(".assist").height() + 100);
          $(".assist-main").height($(window).height() - 230);
        }

        var _resizeTimeout = -1;
        $(window).on("resize", function(){
          window.clearTimeout(_resizeTimeout);
          _resizeTimeout = window.setTimeout(resizeAssist, 200);
        });

        self.loadAssistMain = function(force) {
          self.assist.options.onDataReceived = function (data) {
            if (data.databases) {
              self.assist.mainObjects(data.databases);
              if (force) {
                self.loadAssistFirstLevel(force);
              }
              else if (self.assist.mainObjects().length > 0 && !self.assist.selectedMainObject()) {
                self.assist.selectedMainObject(self.assist.mainObjects()[0]);
                self.loadAssistFirstLevel();
              }
            }
          };
          self.assist.options.onError = function() {
            self.assist.isLoading(false);
          };
          self.assist.getData(null, force);

          self.assist.selectedMainObject.subscribe(function() {
            self.loadAssistFirstLevel();
          });
        };

        self.loadAssistFirstLevel = function(force) {
          var self = this;
          self.assist.options.onDataReceived = function (data) {
            if (data.tables) {
              var _obj = {};
              data.tables.forEach(function (item) {
                _obj[item] = {
                  items: ko.observableArray([]),
                  open: ko.observable(false),
                  loaded: ko.observable(false)
                }
              });
              self.assist.firstLevelObjects(_obj);
            }
            self.assist.isLoading(false);
          };
          self.assist.getData(self.assist.selectedMainObject(), force);
        };

        self.loadAssistSecondLevel = function(first) {
          if (!self.assist.firstLevelObjects()[first].loaded()) {
            self.assist.isLoading(true);
            self.assist.options.onDataReceived = function (data) {
              if (data.columns) {
                var _cols = data.extended_columns ? data.extended_columns : data.columns;
                self.assist.firstLevelObjects()[first].items(_cols);
                self.assist.firstLevelObjects()[first].loaded(true);
              }
              self.assist.isLoading(false);
            };
            self.assist.getData(self.assist.selectedMainObject() + "/" + first);
          }
          self.assist.firstLevelObjects()[first].open(!self.assist.firstLevelObjects()[first].open());
          window.setTimeout(self.resizeAssist, 100);
        };

        self.reloadAssist = function() {
          self.loadAssistMain(true);
        };

        self.showTablePreview = function(table) {
          var tableUrl = "/beeswax/api/table/" + self.assist.selectedMainObject() + "/" + table;
          $("#assistQuickLook").find(".tableName").text(table);
          $("#assistQuickLook").find(".tableLink").attr("href", "/metastore/table/" + self.assist.selectedMainObject() + "/" + table);
          $("#assistQuickLook").find(".sample").empty("");
          $("#assistQuickLook").attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");
          $.ajax({
            url: tableUrl,
            data: {"sample": true},
            beforeSend: function (xhr) {
              xhr.setRequestHeader("X-Requested-With", "Hue");
            },
            dataType: "html",
            success: function (data) {
              $("#assistQuickLook").find(".loader").hide();
              $("#assistQuickLook").find(".sample").html(data);
            },
            error: function (e) {
              if (e.status == 500) {
                $(document).trigger("error", "${ _('There was a problem loading the table preview.') }");
                $("#assistQuickLook").modal("hide");
              }
            }
          });
          $("#assistQuickLook").modal("show");
        };

        if (self.assist.options.baseURL != ""){
          self.loadAssistMain();
        } else {
          self.isAssistVisible(false);
          self.isAssistAvailable(false);
        }
      }

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    }());
  </script>
</%def>

<%def name="jvmMemoryInput()">
  <script type="text/html" id="jvm-memory-input-template">
    <input type="text" class="input-small" data-bind="textInput: value" /> <select class="input-mini" data-bind="options: units, value: selectedUnit" />
  </script>

  <script type="text/javascript" charset="utf-8">
    (function() {
      var JVM_MEM_PATTERN = /([0-9]+)([MG])$/;
      var UNITS = { 'MB' : 'M', 'GB' : 'G' };

      function JvmMemoryInputViewModel(params) {
        this.valueObservable = params.value;
        this.units = Object.keys(UNITS);
        this.selectedUnit = ko.observable();
        this.value = ko.observable().extend({ 'numeric' : 0 });

        var match = JVM_MEM_PATTERN.exec(this.valueObservable());
        if (match.length === 3) {
          this.value(match[1]);
          this.selectedUnit(match[2] === 'M' ? 'MB' : 'GB');
        }

        this.value.subscribe(this.updateValueObservable, this);
        this.selectedUnit.subscribe(this.updateValueObservable, this);
      }

      JvmMemoryInputViewModel.prototype.updateValueObservable = function() {
        if (isNaN(this.value()) || this.value() === '') {
          this.valueObservable(undefined);
        } else {
          this.valueObservable(this.value() + UNITS[this.selectedUnit()]);
        }
      };

      ko.components.register('jvm-memory-input', {
        viewModel: JvmMemoryInputViewModel,
        template: { element: 'jvm-memory-input-template' }
      });
    }());
  </script>
</%def>