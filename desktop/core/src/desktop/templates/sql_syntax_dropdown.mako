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
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
%>

<%def name="sqlSyntaxDropdown()">
  <script type="text/html" id="sql-syntax-dropdown-template">
    <div class="hue-syntax-drop-down" data-bind="style: { 'left': left() + 'px', 'top': top() + 'px' }, component: { name: 'hue-drop-down', params: { value: selected, entries: expected, foreachVisible: false, searchable: false, showOnInit: true, menuOnly: true } }">
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var hideSyntaxDropdown = function () {
        var $sqlSyntaxDropdown = $('#sqlSyntaxDropdown');
        if ($sqlSyntaxDropdown.length > 0) {
          ko.cleanNode($sqlSyntaxDropdown[0]);
          $sqlSyntaxDropdown.remove();
          $(document).off('click', hideOnClickOutside);
        }
      };

      var hideOnClickOutside = function (event) {
        if (jQuery.contains(document, event.target) && !$.contains($('#sqlSyntaxDropdown')[0], event.target) && ($('.modal')[0].length === 0 || !$.contains($('.modal')[0], event.target))) {
          hideSyntaxDropdown();
        }
      };

      function SqlSyntaxDropdownViewModel(params) {
        var self = this;
        self.disposalFunctions = [];
        self.selected = ko.observable();
        var expected = $.map(params.data.expected, function (expected) {
          return expected.text;
        });

        // TODO: Allow suppression of unknown columns etc.
        if (params.data.ruleId) {
          if (expected.length > 0) {
            expected.push({
              divider: true
            });
          }
          expected.push({
            label: window.I18n('Ignore this type of error'),
            suppressRule: params.data.ruleId.toString() + params.data.text.toLowerCase()
          });
        }
        self.expected = ko.observableArray(expected);

        var selectedSub = self.selected.subscribe(function (newValue) {
          if (typeof newValue.suppressRule !== 'undefined') {
            var suppressedRules = window.apiHelper.getFromTotalStorage('hue.syntax.checker', 'suppressedRules', {});
            suppressedRules[newValue.suppressRule] = true;
            window.apiHelper.setInTotalStorage('hue.syntax.checker', 'suppressedRules', suppressedRules);
            huePubSub.publish('editor.refresh.statement.locations', params.snippet);
          } else {
            params.editor.session.replace(params.range, newValue);
          }
          hideSyntaxDropdown();
        });
        self.disposalFunctions.push(function () {
          selectedSub.dispose();
        });

        self.left = ko.observable(params.source.left);
        self.top = ko.observable(params.source.bottom);

        var closeOnEsc = function (e) {
          if (e.keyCode === 27) {
            hideSyntaxDropdown();
          }
        };

        $(document).on('keyup', closeOnEsc);

        self.disposalFunctions.push(function () {
          $(document).off('keyup', closeOnEsc);
        });

        window.setTimeout(function() {
          $(document).on('click', hideOnClickOutside);
        }, 0);

        self.disposalFunctions.push(function () {
          $(document).off('click', hideOnClickOutside);
        })
      }

      SqlSyntaxDropdownViewModel.prototype.dispose = function() {
        var self = this;
        self.disposalFunctions.forEach(function (fn) {
          fn();
        })
      };

      ko.components.register('sql-syntax-dropdown', {
        viewModel: SqlSyntaxDropdownViewModel,
        template: { element: 'sql-syntax-dropdown-template' }
      });

      huePubSub.subscribe('sql.syntax.dropdown.hide', hideSyntaxDropdown);

      huePubSub.subscribe('sql.syntax.dropdown.show', function (details) {
        hideSyntaxDropdown();
        var $sqlSyntaxDropdown = $('<div id="sqlSyntaxDropdown" data-bind="component: { name: \'sql-syntax-dropdown\', params: $data }" />');
        $(HUE_CONTAINER).append($sqlSyntaxDropdown);
        ko.applyBindings(details, $sqlSyntaxDropdown[0]);
      });
    })();
  </script>
</%def>
