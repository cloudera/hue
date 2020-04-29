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

import componentUtils from 'ko/components/componentUtils';
import I18n from 'utils/i18n';

export const DOCUMENT_CONTEXT_FOOTER = 'document-context-footer';

// prettier-ignore
const TEMPLATE = `
<!-- ko if: doc -->
  <!-- ko if: doc.last_modified -->
    <div><span>${I18n('Modified')}</span> <span data-bind="momentFromNow: { data: doc.last_modified, titleFormat: 'LLL Z' }"></span></div>
  <!-- /ko -->
  <!-- ko ifnot: ownedByMe -->
    <div><span>${I18n('Owner')}</span> <span data-bind="text: doc.owner"></span></div>
  <!-- /ko -->
  <!-- ko if: readOnly -->
    <div>${I18n('Read-only')}</div>
  <!-- /ko -->
<!-- /ko -->
`;

class DocumentContextFooter {
  constructor(params) {
    this.doc = params.popoverData.data;
    this.ownedByMe = this.doc && this.doc.owner && this.doc.owner === window.LOGGED_USERNAME;

    this.readOnly = ko.pureComputed(() => {
      if (window.USER_IS_ADMIN || this.ownedByMe) {
        return false;
      }
      const contents = ko.unwrap(params.popoverData.documentContents);
      return contents && !contents.canSave;
    });
  }
}

componentUtils.registerComponent(DOCUMENT_CONTEXT_FOOTER, DocumentContextFooter, TEMPLATE);
