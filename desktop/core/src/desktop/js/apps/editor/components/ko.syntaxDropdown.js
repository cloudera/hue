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

import * as ko from 'knockout';
import $ from 'jquery';

import 'ko/components/ko.dropDown';
import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { hueLocalStorage } from 'utils/storageUtils';

export const SYNTAX_DROPDOWN_COMPONENT = 'sql-syntax-dropdown';
export const SYNTAX_DROPDOWN_ID = 'sqlSyntaxDropdown';
export const SHOW_EVENT = 'sql.syntax.dropdown.show';
export const SHOWN_EVENT = 'sql.syntax.dropdown.shown';
export const HIDE_EVENT = 'sql.syntax.dropdown.hide';

// prettier-ignore
const TEMPLATE = `
<div class="hue-syntax-drop-down" data-bind="
  style: {
    'left': left() + 'px',
    'top': top() + 'px'
  },
  component: {
    name: 'hue-drop-down',
    params: {
      value: selected,
      entries: expected,
      foreachVisible: false,
      searchable: false,
      showOnInit: true,
      menuOnly: true
    }
  }
"></div>
`;

const hideSyntaxDropdown = () => {
  const $sqlSyntaxDropdown = $(`#${SYNTAX_DROPDOWN_ID}`);
  if ($sqlSyntaxDropdown.length) {
    ko.cleanNode($sqlSyntaxDropdown[0]);
    $sqlSyntaxDropdown.remove();
    $(document).off('click', hideOnClickOutside);
  }
};

const hideOnClickOutside = event => {
  const $modal = $('.modal');
  if (
    $.contains(document, event.target) &&
    !$.contains($(`#${SYNTAX_DROPDOWN_ID}`)[0], event.target) &&
    ($modal[0].length === 0 || !$.contains($modal[0], event.target))
  ) {
    hideSyntaxDropdown();
  }
};

class SqlSyntaxDropdownViewModel extends DisposableComponent {
  constructor(params) {
    super();

    this.selected = ko.observable();

    const expected = params.data.expected.map(expected => expected.text);
    // TODO: Allow suppression of unknown columns etc.
    if (params.data.ruleId) {
      if (expected.length > 0) {
        expected.push({
          divider: true
        });
      }
      expected.push({
        label: I18n('Ignore this type of error'),
        suppressRule: params.data.ruleId.toString() + params.data.text.toLowerCase()
      });
    }
    this.expected = ko.observableArray(expected);

    const selectedSub = this.selected.subscribe(newValue => {
      if (typeof newValue.suppressRule !== 'undefined') {
        const suppressedRules = hueLocalStorage('hue.syntax.checker.suppressedRules') || {};
        suppressedRules[newValue.suppressRule] = true;
        hueLocalStorage('hue.syntax.checker.suppressedRules', suppressedRules);
        huePubSub.publish('editor.refresh.statement.locations', params.editorId);
      } else {
        params.editor.session.replace(params.range, newValue);
      }
      hideSyntaxDropdown();
    });

    this.addDisposalCallback(() => {
      selectedSub.dispose();
    });

    this.left = ko.observable(params.source.left);
    this.top = ko.observable(params.source.bottom);

    const closeOnEsc = e => {
      if (e.keyCode === 27) {
        hideSyntaxDropdown();
      }
    };

    $(document).on('keyup', closeOnEsc);

    this.addDisposalCallback(() => {
      $(document).off('keyup', closeOnEsc);
    });

    window.setTimeout(() => {
      $(document).on('click', hideOnClickOutside);
    }, 0);

    this.addDisposalCallback(() => {
      $(document).off('click', hideOnClickOutside);
    });
  }
}

componentUtils.registerComponent(SYNTAX_DROPDOWN_COMPONENT, SqlSyntaxDropdownViewModel, TEMPLATE);

huePubSub.subscribe(HIDE_EVENT, hideSyntaxDropdown);
huePubSub.subscribe(SHOW_EVENT, details => {
  hideSyntaxDropdown();
  const $sqlSyntaxDropdown = $(
    `<div id="${SYNTAX_DROPDOWN_ID}" data-bind="component: { name: '${SYNTAX_DROPDOWN_COMPONENT}', params: $data }"></div>`
  );
  $('body').append($sqlSyntaxDropdown);
  ko.applyBindings(details, $sqlSyntaxDropdown[0]);
  huePubSub.publish(SHOWN_EVENT);
});
