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

import ApiHelper, { LINK_SHARING_PERMS } from '/api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import I18n from 'utils/i18n';
import DisposableComponent from 'ko/components/DisposableComponent';
import { DOCUMENT_UPDATED_EVENT } from 'doc/hueDocument';
import huePubSub from 'utils/huePubSub';

import { HUE_DROP_DOWN_COMPONENT } from 'ko/components/ko.dropDown';

export const NAME = 'link-sharing';

// prettier-ignore
const TEMPLATE = `
  <!-- ko if: window.HAS_LINK_SHARING && perms() -->
  <div class="hue-link-sharing">
    <div style="float: right">
      <!-- ko ifnot: perms().link_sharing_on -->
      <a href="javascript:void(0);" data-test="activate" data-bind="click: createReadLink" title="${ I18n('Share the query via a link') }" >
        <i class="fa fa-wf fa-link"></i> ${ I18n('Get link') }
      </a>
      <!-- /ko -->
      <!-- ko if: perms().link_sharing_on -->
      <a href="javascript:void(0)" data-test="deactivate" data-bind="click: deactivateLink" title="${ I18n('Deactivate the link sharing') }">
        <i class="fa fa-wf fa-link"></i> ${ I18n('Deactivate link') }
      </a>
      <!-- /ko -->
    </div>
    <!-- ko if: perms().link_sharing_on -->
    <div>
      ${ I18n('Any logged in user with the link can') }
      <div class="perm-selector" data-bind="component: {
          name: '${ HUE_DROP_DOWN_COMPONENT }',
          params: {
            value: selectedPerm,
            entries: availablePerms,
            onSelect: changePerm.bind($data)
          }
        }
      "></div>
    </div>
    <div class="input-append">
      <form autocomplete="off">
        <input id="sharedLinkInput" style="width: 520px" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } onfocus="this.select()" data-bind="value: link" type="text" readonly="readonly"/>
        <button class="btn" type="button" data-clipboard-target="#sharedLinkInput" data-bind="clipboard"><i class="fa fa-clipboard"></i></button>
      </form>
    </div>
    <!-- /ko -->
  </div>
  <!-- /ko -->
`;

const OFF_OPTION = { value: LINK_SHARING_PERMS.OFF };
const READ_OPTION = { label: I18n('read'), value: LINK_SHARING_PERMS.READ };
const WRITE_OPTION = { label: I18n('write'), value: LINK_SHARING_PERMS.WRITE };
const AVAILABLE_PERMS = [READ_OPTION, WRITE_OPTION];

class LinkSharing extends DisposableComponent {
  constructor(params) {
    super();
    this.document = params.document;
    this.docDefinition = params.docDefinition;

    this.perms = ko.observable(this.docDefinition.perms);

    this.selectedPerm = ko.observable(this.perms().link_write ? WRITE_OPTION : READ_OPTION);

    this.link = location.origin + window.HUE_BASE_URL + '/hue' + this.docDefinition.absoluteUrl;

    this.availablePerms = AVAILABLE_PERMS;

    super.subscribe(this.perms, perms =>
      this.selectedPerm(perms.link_write ? WRITE_OPTION : READ_OPTION)
    );
  }

  async createReadLink() {
    await this.changePerm(READ_OPTION);
  }

  async deactivateLink() {
    await this.changePerm(OFF_OPTION);
  }

  async changePerm(permOption) {
    const response = await ApiHelper.setLinkSharingPermsAsync({
      perm: permOption.value,
      uuid: this.docDefinition.uuid
    });
    this.perms(response.document.perms);
    huePubSub.publish(DOCUMENT_UPDATED_EVENT, response.document);
  }
}

componentUtils.registerComponent(NAME, LinkSharing, TEMPLATE);
