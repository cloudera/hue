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
import komapping from 'knockout.mapping';

import 'ko/bindings/ko.slideVisible';
import 'ko/bindings/ko.toggle';

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import sessionManager from 'apps/editor/execution/sessionManager';

export const NAME = 'session-panel';
export const SESSION_PANEL_SHOW_EVENT = 'session.panel.show';

const TEMPLATE = `
<div class="session-panel" data-test="${NAME}" data-bind="slideVisible: visible">
  <div class="margin-top-10 padding-left-10 padding-right-10">
    <h4 class="margin-bottom-10"><i class="fa fa-cogs"></i> ${I18n('Sessions')}</h4>
    <div class="session-panel-content">
      <!-- ko ifnot: sessions().length -->
      ${I18n('There are currently no information about the sessions.')}
      <!-- /ko -->
      
      <!-- ko if: sessions().length -->
      <div class="row-fluid">
        <div class="span11">
          <form class="form-horizontal session-config">
            <fieldset>
              <!-- ko foreach: sessions -->
              <div>
                <h4 style="clear:left; display: inline-block">
                  <span data-bind="text: session.type"></span>
                  <!-- ko if: typeof session.session_id != 'undefined' && session.session_id -->
                    <span data-bind="text: session.session_id"></span>
                  <!-- /ko -->
                </h4>
                <div class="session-actions">
                  <a class="inactive-action pointer" title="${I18n(
                    'Re-create session'
                  )}" rel="tooltip" data-bind="click: $parent.restartSession.bind($parent)">
                    <i class="fa fa-refresh" data-bind="css: { 'fa-spin': loading }"></i> ${I18n(
                      'Re-create'
                    )}
                  </a>
                  <a class="inactive-action pointer margin-left-10" title="${I18n(
                    'Close session'
                  )}" rel="tooltip" data-bind="click: $parent.closeSession.bind($parent)">
                    <i class="fa fa-times"></i> ${I18n('Close')}
                  </a>
                  <!-- ko if: window.USE_DEFAULT_CONFIGURATION -->
                    <a class="inactive-action pointer margin-left-10" title="${I18n(
                      'Save session settings as default'
                    )}" rel="tooltip" data-bind="click: saveDefaultUserProperties"><i class="fa fa-save"></i> ${I18n(
  'Set as default settings'
)}</a>
                  <!-- /ko -->
                  <!-- ko if: session.type === 'impala' && typeof session.http_addr != 'undefined' -->
                    <a class="margin-left-10" data-bind="attr: { 'href': session.http_addr }" target="_blank">
                      <span data-bind="text: session.http_addr.replace(/^(https?):\\/\\//, '')"></span> <i class="fa fa-external-link"></i>
                    </a>
                  <!-- /ko -->
                </div>
                <!-- ko if: window.USE_DEFAULT_CONFIGURATION -->
                <div style="width:100%;">
                  <!-- ko component: { name: 'property-selector', params: { properties: properties } } --><!-- /ko -->
                </div>
                <!-- /ko -->
              </div>
              <!-- /ko -->
            </fieldset>
          </form>
        </div>
      </div>
      <!-- /ko -->
    </div>
    <a class="pointer demi-modal-chevron" style="position: absolute; bottom: 0" data-bind="toggle: visible"><i class="fa fa-chevron-up"></i></a>
  </div>
</div>
`;

class EditableProperty {
  constructor(property) {
    this.defaultValue = ko.observableArray(property.defaultValue);
    this.help_text = ko.observable(property.help_text);
    this.key = ko.observable(property.key);
    this.multiple = ko.observable(property.multiple);
    this.nice_name = ko.observable(property.nice_name);
    this.type = ko.observable(property.type);
    this.value = ko.observableArray(property.value);
  }

  getClean() {
    return komapping.toJS(this);
  }
}

class EditableSession {
  constructor(session) {
    this.session = session;
    this.loading = ko.observable(false);
    this.properties = ko.observableArray(
      this.session.properties.map(property => new EditableProperty(property))
    );
  }

  saveDefaultUserProperties() {
    apiHelper.saveConfiguration({
      app: this.session.type,
      properties: this.properties().map(property => property.getClean()),
      userId: window.LOGGED_USER_ID
    });
  }
}

class SessionPanel {
  constructor() {
    this.visible = ko.observable(false);
    this.sessions = ko.observableArray();
    this.activeTypeFilter = undefined;
    huePubSub.subscribe(SESSION_PANEL_SHOW_EVENT, type => this.showSessions(type));
  }

  /**
   *
   * @param {String} typeFilter
   * @return {Promise<void>}
   */
  async showSessions(typeFilter) {
    this.activeTypeFilter = typeFilter;
    let sessions = [];
    if (typeFilter && sessionManager.hasSession(typeFilter)) {
      sessions.push(await sessionManager.getSession({ type: typeFilter }));
    } else {
      sessions = await sessionManager.getAllSessions();
    }
    this.sessions(
      sessions
        .map(session => new EditableSession(session))
        .sort((a, b) => a.session.type.localeCompare(b.session.type))
    );
    this.visible(true);
  }

  /**
   *
   * @param {EditableSession} editableSession
   * @return {Promise<void>}
   */
  async restartSession(editableSession) {
    editableSession.loading(true);
    const session = editableSession.session;
    // Apply any changed properties
    session.properties = editableSession
      .properties()
      .map(editableProperty => editableProperty.getClean());
    await sessionManager.restartSession(session);
    await this.showSessions(this.activeTypeFilter);
  }

  /**
   *
   * @param {EditableSession} editableSession
   * @return {Promise<void>}
   */
  async closeSession(editableSession) {
    editableSession.loading(true);
    const session = editableSession.session;
    await sessionManager.closeSession(session);
    await this.showSessions(this.activeTypeFilter);
  }

  saveDefaultUserProperties(session) {}
}

componentUtils.registerComponent(NAME, SessionPanel, TEMPLATE);
