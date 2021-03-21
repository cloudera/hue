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

import 'ko/bindings/ko.publish';

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { SHOW_EVENT as SHOW_GIST_MODAL_EVENT } from 'ko/components/ko.shareGistModal';
import { DIALECT, STATUS } from 'apps/editor/snippet';

const TEMPLATE = `
<div class="snippet-editor-actions">
  <div class="btn-group">
    <button class="btn btn-mini btn-editor dropdown-toggle" data-toggle="dropdown">
      <i class="fa fa-fw fa-ellipsis-v"></i> ${I18n('More')}
      <span class="caret"></span>
    </button>
    <ul class="dropdown-menu pull-right" style="position: fixed !important; transform: translateX(-143px); left: initial; right: initial; top: initial; bottom: initial;">
      <li>
        <a href="javascript:void(0)" data-bind="click: explain, css: {'disabled': !explainEnabled() }" title="${I18n(
          'Explain the current SQL query'
        )}">
          <i class="fa fa-fw fa-map-o"></i> ${I18n('Explain')}
        </a>
      </li>
      <!-- ko if: window.HAS_GIST -->
      <li>
        <a href="javascript:void(0)" data-bind="click: createGist, css: { 'disabled': !createGistEnabled() }" title="${I18n(
          'Share the query selection via a link'
        )}">
          <i class="fa fa-fw fa-link"></i> ${I18n('Get shareable link')}
        </a>
      </li>
      <!-- /ko -->
      <li>
        <a href="javascript:void(0)" data-bind="click: format, css: { 'disabled': !formatEnabled() }" title="${I18n(
          'Format the current SQL query'
        )}">
          <i class="fa fa-fw fa-indent"></i> ${I18n('Format')}
        </a>
      </li>
      <li>
        <a href="javascript:void(0)" data-bind="click: clear, css: {'disabled': !clearEnabled() }" title="${I18n(
          'Clear the current editor'
        )}">
          <i class="fa fa-fw fa-eraser"></i> ${I18n('Clear')}
        </a>
      </li>
      <li>
        <a href="javascript:void(0)" data-bind="toggle: snippet.settingsVisible, visible: snippet.hasProperties" title="${I18n(
          'Query settings'
        )}">
          <i class="fa fa-fw fa-cog"></i> ${I18n('Settings')}
        </a>
      </li>
    </ul>
  </div>
</div>
`;

class SnippetEditorActions {
  constructor(params) {
    this.snippet = params.snippet;

    this.clearEnabled = this.snippet.isReady;

    this.compatibilityEnabled = ko.pureComputed(
      () => this.snippet.dialect() === DIALECT.hive || this.snippet.dialect() === DIALECT.impala
    );

    this.createGistEnabled = ko.pureComputed(
      () => this.snippet.isSqlDialect() && this.snippet.statement() !== ''
    );

    this.explainEnabled = ko.pureComputed(
      () =>
        this.snippet.isReady() &&
        this.snippet.statement() !== '' &&
        this.snippet.status() !== STATUS.running &&
        this.snippet.status() !== STATUS.loading
    );

    this.formatEnabled = ko.pureComputed(
      () =>
        this.snippet.isReady() &&
        this.snippet.isSqlDialect() &&
        this.snippet.statement_raw() &&
        this.snippet.statement_raw().length < 400000
    );
  }

  checkCompatibility() {
    if (!this.compatibilityEnabled()) {
      return;
    }
    hueAnalytics.log('notebook', 'compatibility');

    // TODO: Move compatibility check logic here
    this.snippet.checkCompatibility();
  }

  clear() {
    if (!this.clearEnabled()) {
      return;
    }
    hueAnalytics.log('notebook', 'clear');

    this.snippet.ace().setValue('', 1);
    this.snippet.result.clear();
    this.snippet.status(STATUS.ready);
  }

  async explain() {
    if (!this.explainEnabled()) {
      return;
    }
    hueAnalytics.log('notebook', 'explain');

    this.snippet.explanation('');
    const explanation = await apiHelper.explainAsync({ snippet: this.snippet });
    this.snippet.explanation(explanation);
    this.snippet.currentQueryTab('queryExplain');
  }

  async createGist() {
    if (!this.createGistEnabled()) {
      return;
    }
    hueAnalytics.log('notebook', 'createGist');

    const gistLink = await apiHelper.createGistAsync({
      statement:
        this.snippet.ace().getSelectedText() != ''
          ? this.snippet.ace().getSelectedText()
          : this.snippet.statement_raw(),
      doc_type: this.snippet.dialect(),
      name: this.snippet.name(),
      description: ''
    });

    huePubSub.publish(SHOW_GIST_MODAL_EVENT, { link: gistLink });
  }

  format() {
    if (!this.formatEnabled()) {
      return;
    }

    hueAnalytics.log('notebook', 'format');
    apiHelper
      .formatSql({
        statements:
          this.snippet.ace().getSelectedText() !== ''
            ? this.snippet.ace().getSelectedText()
            : this.snippet.statement_raw()
      })
      .done(data => {
        if (data.status === 0) {
          if (this.snippet.ace().getSelectedText() !== '') {
            this.snippet
              .ace()
              .session.replace(
                this.snippet.ace().session.selection.getRange(),
                data.formatted_statements
              );
          } else {
            this.snippet.statement_raw(data.formatted_statements);
            this.snippet.ace().setValue(this.snippet.statement_raw(), 1);
          }
        } else {
          this.snippet.handleAjaxError(data);
        }
      });
  }

  dispose() {}
}

componentUtils.registerComponent('snippet-editor-actions', SnippetEditorActions, TEMPLATE);
