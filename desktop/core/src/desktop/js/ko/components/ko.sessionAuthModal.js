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

import $ from 'jquery';
import * as ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import sessionManager from 'apps/editor/execution/sessionManager';

export const SHOW_EVENT = 'show.session.auth.modal';
export const SHOWN_EVENT = 'session.auth.modal.shown';

const TEMPLATE = `
<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-label="${I18n(
    'Close'
  )}"><span aria-hidden="true">&times;</span></button>
  <h2 class="modal-title">${I18n('Connect to the data source')}</h2>
</div>
<div class="modal-body">
  <!-- ko if: authSessionMessage -->
    <div class="row-fluid">
      <div class="alert-warning">
        <span data-bind="text: authSessionMessage"></span>
      </div>
    </div>
  <!-- /ko -->
  <div class="row-fluid">
    <div class="span6">
      <div class="input-prepend">
        <span class="add-on muted"><i class="fa fa-user"></i></span>
        <input name="username" data-test="usernameInput" type="text" data-bind="textInput: authSessionUsername" placeholder="${I18n(
          'Username'
        )}"/>
      </div>
    </div>
    <div class="span6">
      <div class="input-prepend">
        <span class="add-on muted"><i class="fa fa-lock"></i></span>
        <input name="password" data-test="passwordInput" type="password" data-bind="textInput: authSessionPassword" placeholder="${I18n(
          'Password'
        )}"/>
      </div>
    </div>
  </div>
</div>
<div class="modal-footer">
  <a class="btn" data-dismiss="modal">${I18n('Cancel')}</a>
  <a class="btn btn-primary disable-feedback" data-bind="click: connect, css: { 'disabled': loading }"><i class='fa fa-spinner fa-spin' data-bind="visible: loading"></i> ${I18n(
    'Connect'
  )}</a>
</div>
`;

class SessionAuthModal {
  constructor(params, $modal) {
    this.pending = true;
    this.loading = ko.observable(false);
    this.reject = params.reject;
    this.resolve = params.resolve;
    this.session = params.session;
    this.authSessionMessage = params.message;
    this.$modal = $modal;

    let username = '';
    this.session.properties.some(property => {
      if (property.name === 'user') {
        username = property.value;
      }
    });
    this.authSessionUsername = ko.observable(username);
    this.authSessionPassword = ko.observable();
  }

  async connect() {
    this.loading(true);
    const properties = this.session.properties.filter(
      property => property.name !== 'user' && property.name !== 'password'
    );
    properties.push({ name: 'user', value: this.authSessionUsername() });
    properties.push({ name: 'password', value: this.authSessionPassword() });
    try {
      const session = await sessionManager.createDetachedSession({
        type: this.session.type,
        properties: properties,
        preventAuthModal: true
      });
      // The modal could be closed before creation
      if (this.pending) {
        this.resolve(session);
      }
      this.pending = false;
      this.$modal.modal('hide');
    } catch (reason) {
      if (reason && reason.auth) {
        this.authSessionMessage(reason.message);
      }
    }
    this.loading(false);
  }
}

componentUtils.registerComponent('session-auth-modal', undefined, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_EVENT, sessionAuthParams => {
    let $sessionAuthModal = $('#sessionAuthModal');
    if ($sessionAuthModal.length > 0) {
      ko.cleanNode($sessionAuthModal[0]);
      $sessionAuthModal.remove();
    }

    $sessionAuthModal = $(
      '<div id="sessionAuthModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'session-auth-modal\', params: params }" data-keyboard="true" class="modal hide fade" tabindex="-1"></div>'
    );
    $('body').append($sessionAuthModal);

    const model = new SessionAuthModal(sessionAuthParams, $sessionAuthModal);
    const data = {
      params: model,
      descendantsComplete: () => {
        huePubSub.publish(SHOWN_EVENT, $sessionAuthModal[0]);
      }
    };

    ko.applyBindings(data, $sessionAuthModal[0]);
    $sessionAuthModal.modal('show');
    $sessionAuthModal.on('hidden', () => {
      if (model.pending) {
        model.reject();
        model.pending = false;
      }
    });
  });
});
