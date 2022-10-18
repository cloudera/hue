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

import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import HueFileEntry from 'doc/hueFileEntry';
import DisposableComponent from 'ko/components/DisposableComponent';

import './ko.linkSharing';
import { REFRESH_DOC_ASSIST_EVENT } from 'ko/components/assist/ko.assistDocumentsPanel';

export const SHOW_EVENT = 'doc.show.share.modal';
export const SHOWN_EVENT = 'doc.share.modal.shown';

// prettier-ignore
const TEMPLATE = `
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ I18n('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ I18n('Sharing') } - <span data-bind="text: documentName"></span></h2>
    </div>
    <div class="modal-body" style="overflow: visible;">
      <!-- ko with: document -->
        <!-- ko with: definition -->
          <!-- ko component: {
            name: 'link-sharing',
            params: {
              document: $parent,
              docDefinition: $data
            }
          } --><!-- /ko -->
          <div class="row-fluid" data-bind="visible: !$parent.hasErrors()"  id="scrolldiv">
            <div class="span6">
              <h4 class="muted" style="margin-top: 0">${ I18n('Read') }</h4>
              <div data-bind="visible: (perms.read.users.length == 0 && perms.read.groups.length == 0)">${ I18n('The document is not shared for read.') }</div>
              <ul class="unstyled airy" style="max-height: 20vh; overflow-x:auto;" data-bind="foreach: perms.read.users">
                <li>
                  <span class="badge badge-info" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-user"></i> <span data-bind="text: $parents[1].prettifyUsernameById(id), attr:{'data-id': id}"></span></span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeUserReadShare($data) }"> <i class="fa fa-times"></i></span>
                </li>
              </ul>
              <ul class="unstyled airy" style="max-height: 20vh; overflow-x:auto;" data-bind="foreach: perms.read.groups">
                <li>
                  <span class="badge badge-info" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-users"></i> ${ I18n('Group') } &quot;<span data-bind="text: name"></span>&quot;</span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeGroupReadShare($data) }"> <i class="fa fa-times"></i></span>
                </li>
              </ul>
            </div>

            <div class="span6">
              <h4 class="muted" style="margin-top: 0">${ I18n('Modify') }</h4>
              <div data-bind="visible: (perms.write.users.length == 0 && perms.write.groups.length == 0)">${ I18n('The document is not shared for modify.') }</div>
              <ul class="unstyled airy" style="max-height: 20vh; overflow-x:auto;" data-bind="foreach: perms.write.users">
                <li>
                  <span class="badge badge-info badge-left" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }">
                    <i class="fa fa-user">
                    </i>
                    <span data-bind="text: $parents[1].prettifyUsernameById(id), attr:{'data-id': id}">
                    </span>
                  </span>
                  <span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeUserWriteShare($data) }">
                    <i class="fa fa-times"></i>
                  </span>
                </li>
              </ul>
              <ul class="unstyled airy" style="max-height: 20vh; overflow-x:auto;" data-bind="foreach: perms.write.groups">
                <li>
                  <span class="badge badge-info badge-left" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }">
                    <i class="fa fa-users"></i> ${ I18n('Group') } &quot;
                    <span data-bind="text: name"></span>&quot;</span>
                    <span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeGroupWriteShare($data) }">
                    <i class="fa fa-times"></i>
                  </span>
                </li>
              </ul>
            </div>
          </div>
        <!-- /ko -->
        <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: loading">
          <i class="fa fa-spinner fa-spin fa-2x" style="color: #999;"></i>
        </div>
        <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: hasErrors() && ! loading()">
          ${ I18n('There was an error loading the document.')}
        </div>
        <div style="margin-top: 20px" data-bind="visible: fileEntry.canModify() && ! hasErrors() && ! loading()">
          <div id="shareDocAutocompleteMenu"></div>
          <div class="input-append" style="font-size: inherit">
            <input id="shareDocUserInput" placeholder="${ I18n('Type a username or a group name') }" type="text" data-bind="
                autocomplete: {
                  source: shareAutocompleteUserSource.bind($data),
                  select: function(event,ui) { onShareAutocompleteSelectEnter(event,ui);},
                  itemTemplate: 'user-search-autocomp-item',
                  noMatchTemplate: 'user-search-autocomp-no-match',
                  valueObservable: searchInput,
                  showSpinner: true,
                  classPrefix: 'hue-',
                  onEnter: onShareAutocompleteUserEnter.bind($data),
                  appendTo: '#shareDocAutocompleteMenu'
                },
                clearable: {
                  value: searchInput,
                  textInput: searchInput
                }
              " class="ui-autocomplete-input" autocomplete="off" style="width: 476px">
            <div class="btn-group" style="overflow:visible; margin-left: -4px;">
              <a id="documentShareAddBtn" class="btn" style="border-radius: 0" data-bind="click: function () {  onShareAutocompleteUserEnter() }">
                <span data-bind="text: selectedPerm() == 'read' ? '${ I18n('Read') }' : '${ I18n('Modify') }'">
                </span>
              </a>
              <a id="documentShareCaret" class="btn dropdown-toggle" data-toggle="dropdown">
               <span class="caret"></span>
              </a>
              <ul class="dropdown-menu">
                <li>
                  <a data-bind="click: function () { selectedPerm('read'); onShareAutocompleteUserEnter() }" href="javascript:void(0)">
                    <i class="fa fa-plus"></i> ${ I18n('Read') }
                  </a>
                </li>
                <li>
                  <a data-bind="click: function () { selectedPerm('write'); onShareAutocompleteUserEnter() }" href="javascript:void(0)">
                    <i class="fa fa-plus"></i> ${ I18n('Modify') }
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      <!-- /ko -->
    </div>
    <div class="modal-footer">
      <a href="#" data-dismiss="modal" class="btn disable-feedback disable-enter">${ I18n('Close') }</a>
    </div>
`;

class ShareDocModal extends DisposableComponent {
  constructor(params) {
    super();
    this.document = ko.observable();
    this.perms = ko.observable();
    this.uuid = ko.observable();

    this.wasSharedBefore = undefined;

    this.documentName = ko.pureComputed(() => this.document() && this.document().definition().name);
    this.showLinkSharing = ko.pureComputed(
      () => window.HAS_LINK_SHARING && this.perms() && this.perms().link_sharing_on
    );

    this.initDocument(params);
  }

  dispose() {
    if (this.wasSharedBefore !== this.document().isShared()) {
      huePubSub.publish(REFRESH_DOC_ASSIST_EVENT);
    }
  }

  async initDocument(params) {
    try {
      const document = await getDocument(params);
      this.wasSharedBefore = document.isShared();
      this.document(document);
      this.perms(document.definition().perms);
      this.uuid(document.definition().uuid);
    } catch (err) {
      console.warn('Failed loading document.');
      console.error(err);
    }
  }
}

const getDocument = async params =>
  new Promise(async (resolve, reject) => {
    const ensureLoaded = async entry => entry.document() || (await entry.loadDocument());

    if (typeof params === 'string') {
      const entry = new HueFileEntry({
        activeEntry: ko.observable(),
        trashEntry: ko.observable(),
        app: 'documents',
        activeSort: ko.observable(),
        user: window.LOGGED_USERNAME,
        definition: {
          uuid: params
        }
      });
      entry.load(async () => {
        resolve(await ensureLoaded(entry));
      }, reject);
    } else {
      resolve(await ensureLoaded(params));
    }
  });

componentUtils.registerComponent('share-doc-modal', ShareDocModal, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_EVENT, async params => {
    let $shareDocMocal = $('#shareDocModal');
    if ($shareDocMocal.length) {
      ko.cleanNode($shareDocMocal[0]);
      $shareDocMocal.remove();
    }

    $shareDocMocal = $(
      '<div id="shareDocModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'share-doc-modal\', params: params }" data-keyboard="true" class="modal hide fade" tabindex="-1"></div>'
    );
    $('body').append($shareDocMocal);

    const data = {
      params: params,
      descendantsComplete: () => {
        huePubSub.publish(SHOWN_EVENT);
      }
    };

    ko.applyBindings(data, $shareDocMocal[0]);
    $shareDocMocal.modal('show');
    $shareDocMocal.on('hide', () => {
      ko.cleanNode($shareDocMocal[0]);
      $shareDocMocal.remove();
    });
  });
});
