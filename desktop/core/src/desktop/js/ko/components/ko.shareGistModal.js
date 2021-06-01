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

import ApiHelper from '/api/apiHelper';
import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import DisposableComponent from 'ko/components/DisposableComponent';

export const SHOW_EVENT = 'show.share.gist.modal';
export const SHOWN_EVENT = 'share.gist.modal.shown';

// prettier-ignore
const TEMPLATE = `
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ I18n('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ I18n('Shareable link') }</h2>
  </div>
  <div class="modal-body">
    <div class="row-fluid">
      <div class="input-append">
        <form autocomplete="off">
          <input id="gistLink" style="width: 510px" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } onfocus="this.select()" data-bind="value: link" type="text" placeholder="${ I18n('Link') }" readonly="readonly"/>
          <button class="btn" type="button" data-dismiss="modal" data-clipboard-target="#gistLink" data-bind="clipboard"><i class="fa fa-clipboard"></i></button>
        </form>
      </div>
    </div>
    <!-- ko if: window.SHARE_TO_SLACK -->
    <label class="checkbox"><input type="checkbox" data-bind="checked: showSlackSection"> ${ I18n('Share to Slack') } </input></label>
    <!-- ko if: showSlackSection -->
    <form class="form-horizontal">
      <div class="control-group">
        <label class="control-label">${ I18n('Message') }</label>
        <div class="controls">
          <input type="text" style="width: 245px" data-bind="value: messageDescription, valueUpdate:'afterkeydown'" placeholder="${ I18n('(Optional)') }"/>
        </div>
      </div>
      <div class="control-group">
        <label class="control-label">${ I18n('Channel') }</label>
        <div class="controls">
          <select class="input-xlarge" data-bind="options: channels, optionsCaption: 'Choose...', value: selectedChannel"></select>
          <button class="btn" type="button" data-dismiss="modal" data-bind="click: postMessage">${ I18n('Send') }</button>
        </div>
      </div>
    </form>
  <!-- /ko -->
  <!-- /ko -->
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${ I18n('Close') }</a>
  </div>
`;

class ShareGistModal extends DisposableComponent {
  constructor(params) {
    super();
    this.showSlackSection = ko.observable(false);

    this.link = ko.observable(params.link);
    this.channels = ko.observableArray(params.channels);

    this.selectedChannel = ko.observable('');
    this.messageDescription = ko.observable('');
  }

  async postMessage() {
    try {
      await ApiHelper.sendSlackMessageAsync({
        channel: this.selectedChannel,
        message: this.messageDescription() + '\n' + this.link()
      });
    } catch (err) {
      console.warn('Failed posting message in Slack channel');
      console.error(err);
    }
  }
}

componentUtils.registerComponent('share-gist-modal', undefined, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_EVENT, async params => {
    let $shareGistModal = $('#shareGistModal');
    if ($shareGistModal.length) {
      ko.cleanNode($shareGistModal[0]);
      $shareGistModal.remove();
    }

    $shareGistModal = $(
      '<div id="shareGistModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'share-gist-modal\', params: params }" data-keyboard="true" class="modal hide fade" tabindex="-1"></div>'
    );
    $('body').append($shareGistModal);

    const data = {
      params: new ShareGistModal(params),
      descendantsComplete: () => {
        huePubSub.publish(SHOWN_EVENT);
      }
    };

    ko.applyBindings(data, $shareGistModal[0]);
    $shareGistModal.modal('show');
  });
});
