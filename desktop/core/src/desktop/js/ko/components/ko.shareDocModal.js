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
import HueFileEntry from 'doc/hueFileEntry';

export const SHOW_EVENT = 'doc.show.share.modal';
export const SHOWN_EVENT = 'doc.share.modal.shown';

// prettier-ignore
const TEMPLATE = `
  <!-- ko with: document -->
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ I18n('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ I18n('Sharing') } - <span data-bind="text: $parent.definition().name"></span></h2>
  </div>
  <div class="modal-body" style="overflow: visible; height: 240px">

    <!-- ko if: window.HAS_LINK_SHARING -->
    <a href="javascript:void(0)" data-bind="visible: !$parent.definition().perms.link_sharing_on" title="${ I18n(
      'Share the query via a link'
    ) }">
      <i class="fa fa-wf fa-link"></i> ${ I18n('Get link') }
    </a>

    <!-- ko with: $parent.definition().perms.link_sharing_on -->
    <a href="javascript:void(0)" title="${ I18n(
      'Deactivate the link sharing'
    ) }">
      <i class="fa fa-wf fa-link"></i> ${ I18n('Deactivate link') }
    </a>

    <div class="row-fluid">
      <div class="span12">
        Anyone logged and with the link can:
        <br/>
        Read: <span data-bind="text: $parent.definition().perms.link_read"></span> | Write: <span data-bind="text: $parent.definition().perms.link_write"></span>
        <h4 class="muted" style="margin-top: 0">${ I18n('Shareable link') }</h4>
        <div class="input-group">
          <input class="input-xxlarge" onfocus="this.select()" name="gist-link" id="gist-link" type="text" placeholder="${ I18n('Link') }"/>
        </div>
        <div class="input-prepend">
          <a class="btn gist-link-btn" data-clipboard-target="#gist-link" data-dismiss="modal">${ I18n('Copy')}</a>
          <button class="add-on muted gist-link-btn" data-clipboard-target="#gist-link">
            <i class="fa fa-clipboard"></i>
          </button>
        </div>
      </div>
    </div>
    <!-- /ko -->
    <!-- /ko -->

    <!-- ko with: definition -->
    <div class="row-fluid" data-bind="visible: !$parent.hasErrors()" style="max-height: 114px;" id="scrolldiv">
      <div class="span6">
        <h4 class="muted" style="margin-top: 0">${ I18n('Read') }</h4>
        <div data-bind="visible: (perms.read.users.length == 0 && perms.read.groups.length == 0)">${ I18n('The document is not shared for read.') }</div>
        <ul class="unstyled airy" data-bind="foreach: perms.read.users">
          <li>
            <span class="badge badge-info" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-user"></i> <span data-bind="text: $parents[1].prettifyUsernameById(id), attr:{'data-id': id}"></span></span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeUserReadShare($data) }"> <i class="fa fa-times"></i></span>
          </li>
        </ul>
        <ul class="unstyled airy" data-bind="foreach: perms.read.groups">
          <li>
            <span class="badge badge-info" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-users"></i> ${ I18n('Group') } &quot;<span data-bind="text: name"></span>&quot;</span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeGroupReadShare($data) }"> <i class="fa fa-times"></i></span>
          </li>
        </ul>
      </div>

      <div class="span6">
        <h4 class="muted" style="margin-top: 0">${ I18n('Modify') }</h4>
        <div data-bind="visible: (perms.write.users.length == 0 && perms.write.groups.length == 0)">${ I18n('The document is not shared for modify.') }</div>
        <ul class="unstyled airy" data-bind="foreach: perms.write.users">
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
        <ul class="unstyled airy" data-bind="foreach: perms.write.groups">
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
          " class="ui-autocomplete-input" autocomplete="off" style="width: 420px">
        <div class="btn-group" style="overflow:visible">
          <a id="documentShareAddBtn" class="btn" data-bind="click: function () {  onShareAutocompleteUserEnter() }">
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
  </div>
  <div class="modal-footer">
    <a href="#" data-dismiss="modal" class="btn disable-feedback disable-enter">${ I18n('Close') }</a>
  </div>
  <!-- /ko -->
`;

const getEntry = async params =>
  new Promise(resolve => {
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
      entry.load(
        () => {
          resolve(entry);
        },
        () => {
          resolve(entry);
        }
      );
    } else {
      resolve(params);
    }
  });

componentUtils.registerComponent('share-doc-modal', undefined, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_EVENT, async params => {
    const hueFileEntry = await getEntry(params);

    let $shareDocMocal = $('#shareDocModal');
    if ($shareDocMocal.length) {
      ko.cleanNode($shareDocMocal[0]);
      $shareDocMocal.remove();
    }

    let isSharedBefore;

    if (!hueFileEntry.document()) {
      hueFileEntry.loadDocument(() => {
        isSharedBefore = hueFileEntry.document().isShared();
      });
    } else {
      isSharedBefore = hueFileEntry.document().isShared();
    }

    $shareDocMocal = $(
      '<div id="shareDocModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'share-doc-modal\', params: params }" data-keyboard="true" class="modal hide fade" tabindex="-1"/>'
    );
    $('body').append($shareDocMocal);

    const data = {
      params: hueFileEntry,
      descendantsComplete: () => {
        huePubSub.publish(SHOWN_EVENT);
      }
    };

    ko.applyBindings(data, $shareDocMocal[0]);
    $shareDocMocal.modal('show');
    $shareDocMocal.on('hide', () => {
      if (isSharedBefore !== hueFileEntry.document().isShared()) {
        huePubSub.publish('assist.document.refresh');
      }
    });
  });
});
