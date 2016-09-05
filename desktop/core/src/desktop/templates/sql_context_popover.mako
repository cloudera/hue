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
from metadata.conf import has_navigator
%>

<%def name="sqlContextPopover()">
  <style>
    .sql-context-popover {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1060;
      display: block;
      width: 450px;
      height: 300px;
      padding: 1px;
      text-align: left;
      text-align: start;
      background-color: #fff;
      -webkit-background-clip: padding-box;
      background-clip: padding-box;
      border: 1px solid transparent;
    }

    .sql-context-popover.sql-context-popover-top {
      margin-top: -5px;
    }

    .sql-context-popover.sql-context-popover-top .sql-context-popover-arrow {
      bottom: -6px;
      left: 50%;
      margin-left: -6px;
      border-top-color: #338BB8;
      border-bottom-width: 0;
    }

    .sql-context-popover.sql-context-popover-top .sql-context-popover-arrow::after {
      bottom: 1px;
      margin-left: -3px;
      content: "";
      border-top-color: #338BB8;
      border-bottom-width: 0;
    }

    .sql-context-popover.sql-context-popover-right {
      margin-left: 5px;
    }

    .sql-context-popover.sql-context-popover-right .sql-context-popover-arrow {
      top: 50%;
      left: -6px;
      margin-top: -6px;
      border-right-color: #338BB8;
      border-left-width: 0;
    }

    .sql-context-popover.sql-context-popover-right .sql-context-popover-arrow::after {
      bottom: -3px;
      left: 1px;
      content: "";
      border-right-color: #338BB8;
      border-left-width: 0;
    }

    .sql-context-popover.sql-context-popover-bottom {
      margin-top: 7px;
    }

    .sql-context-popover.sql-context-popover-bottom .sql-context-popover-arrow {
      top: -6px;
      left: 50%;
      margin-left: -6px;
      border-top-width: 0;
      border-bottom-color: #338BB8;
    }

    .sql-context-popover.sql-context-popover-bottom .sql-context-popover-arrow::after {
      top: 3px;
      margin-left: -3px;
      content: "";
      border-top-width: 0;
      border-bottom-color: #338BB8;
    }

    .sql-context-popover.sql-context-popover-left {
      margin-left: -5px;
    }

    .sql-context-popover.sql-context-popover-left .sql-context-popover-arrow {
      top: 50%;
      right: -6px;
      margin-top: -3px;
      border-right-width: 0;
      border-left-color: #338BB8;
    }

    .sql-context-popover.sql-context-popover-left .sql-context-popover-arrow::after {
      right: 2px;
      bottom: -3px;
      content: "";
      border-right-width: 0;
      border-left-color: #338BB8;
    }

    .sql-context-popover-title {
      padding: 6px 10px;
      margin: 0;
      font-size: 0.9rem;
      background-color: #fff;
      border-bottom: 1px solid #ebebeb;
    }

    .sql-context-popover-title:empty {
      display: none;
    }

    .sql-context-popover-content {
      padding: 9px 14px;
    }

    .sql-context-popover-arrow, .sql-context-popover-arrow::after {
      position: absolute;
      display: block;
      width: 0;
      height: 0;
      border-color: transparent;
      border-style: solid;
    }

    .sql-context-popover-arrow {
      border-width: 6px;
    }

    .popover-arrow::after {
      content: "";
      border-width: 5px;
    }
  </style>

  <script type="text/html" id="sql-context-popover-template">
    <div class="sql-context-popover sql-context-popover-bottom" data-bind="css: orientationClass, style: { left: left() + 'px', top: top() + 'px' }">
      <div class="sql-context-popover-arrow"></div>
      <div class="sql-context-popover-title">
        <i class="pull-left fa muted" data-bind="css: iconClass" style="margin-top: 3px"></i> <span data-bind="text: title"></span>
      </div>
      <div class="sql-context-popover-content">
        <pre data-bind="text: ko.mapping.toJSON(data)"></pre>
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    require(['knockout'], function (ko) {

      var hidePopover = function () {
        $('#sqlContextPopover').remove();
        $(document).off('click', hideOnClickOutside);
      };

      var hideOnClickOutside = function (event) {
        if (!$.contains($('#sqlContextPopover')[0], event.target)) {
          hidePopover();
        }
      };

      function sqlContextPopoverViewModel(params) {
        var self = this;
        self.left = ko.observable();
        self.top = ko.observable();
        self.data = params.data;
        var orientation = params.orientation || 'bottom';

        switch (orientation) {
          case 'left':
            break;
          case 'top':
            self.left(params.source.left + Math.round((params.source.right - params.source.left) / 2) - 225);
            self.top(params.source.top - 300);
            break;
          case 'right':
            break;
          case 'bottom':
            self.left(params.source.left + Math.round((params.source.right - params.source.left) / 2) - 225);
            self.top(params.source.bottom);
        }

        self.isTable = params.data.type === 'table';
        self.isColumn = params.data.type === 'column';
        self.isFunction = params.data.type === 'function';

        if (self.isTable) {
          self.title = params.data.identifierChain[params.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-table'
        } else if (self.isColumn) {
          self.title = params.data.identifierChain[params.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-columns'
        } else if (self.isFunction) {
          self.title = params.data.function;
          self.iconClass = 'fa-superscript'
        } else {
          self.title = '';
          self.iconClass = 'fa-info'
        }
        self.orientationClass = 'sql-context-popover-' + orientation;
      }

      sqlContextPopoverViewModel.prototype.dispose = function () {
        hidePopover();
      };

      ko.components.register('sql-context-popover', {
        viewModel: sqlContextPopoverViewModel,
        template: { element: 'sql-context-popover-template' }
      });

      huePubSub.subscribe('sql.context.popover.hide', hidePopover);

      huePubSub.subscribe('sql.context.popover.show', function (details) {
        hidePopover();
        var $sqlContextPopover = $('<div id="sqlContextPopover" data-bind="component: { name: \'sql-context-popover\', params: { data: data, source: source } }" />');
        $('body').append($sqlContextPopover);
        ko.applyBindings(details, $sqlContextPopover[0]);
        window.setTimeout(function() {
          $(document).on('click', hideOnClickOutside);
        }, 0);
      })
    });
  </script>
</%def>