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

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';
import { ASSIST_DOC_HIGHLIGHT_EVENT } from 'ko/components/assist/events';

const TEMPLATE_NAME = 'context-document-details';

// prettier-ignore
export const DOCUMENT_CONTEXT_TEMPLATE = `
<script type="text/html" id="${ TEMPLATE_NAME }">
  <div class="context-popover-flex-fill" style="overflow: auto;">
    <div class="context-popover-inner-content">
      <div style="position: absolute; right: 6px; top: 8px;">
        <a class="pointer inactive-action" data-bind="visible: !$parent.closeDisabled, click: function () { $parent.close() }"><i class="fa fa-fw fa-times"></i></a>
      </div>
      <!-- ko if: typeof documentContents() !== 'undefined' && typeof documentContents().snippets !== 'undefined' -->
      <!-- ko with: details -->
      <div class="context-popover-doc-header-link" ><a href="javascript:void(0)" data-bind="hueLink: link, click: function () { $parents[1].close(); }"><!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: false } } --><!-- /ko --> <span data-bind="text:name"></span></a></div>
      <!-- ko if: description -->
      <div class="context-popover-doc-description" data-bind="toggleOverflow: { height: 60 }"><div data-bind="text: description"></div></div>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko with: documentContents -->
      <!-- ko foreach: snippets -->
      <div class="context-popover-doc-contents" data-bind="highlight: { value: statement_raw, formatted: true, dialect: type }"></div>
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: typeof documentContents() === 'undefined' || typeof documentContents().snippets === 'undefined' -->
      <div style="width: 100%;" data-bind="template: { name: 'generic-document-context-template', data: details }"></div>
      <!-- /ko -->
    </div>
  </div>
</script>

<script type="text/html" id="generic-document-context-template">
  <div style="width:100%; text-align: center; margin-top: 40px; font-size: 100px; color: #787878;" data-bind="template: { name: 'document-icon-template', data: { document: { isDirectory: type === 'directory', definition: function() { return $data } } } }"></div>
  <div style="width: 100%; margin-top: 20px; text-align:center">
    <!-- ko if: type === 'directory' -->
    <a style="font-size: 20px;" href="javascript:void(0)" data-bind="text: name, publish: 'context.popover.show.in.assist'"></a>
    <!-- /ko -->
    <!-- ko if: type !== 'directory' -->
    <a style="font-size: 20px;" href="javascript:void(0)" data-bind="text: name, hueLink: link, click: function () { $parents[1].close(); }"></a>
    <!-- /ko -->
    <br/>
    <span data-bind="text: window.DOCUMENT_TYPE_I18n[type] || type"></span>
    <!-- ko if: description -->
    <div class="context-popover-doc-description" data-bind="text: description"></div>
    <!-- /ko -->
  </div>
</script>
`;

class DocumentContext {
  constructor(data) {
    const self = this;
    self.disposals = [];

    // Adapt some details to a common format, the global search endpoint has different structure than the docs one
    self.details = {
      type: data.doc_type || data.type,
      name: data.originalName || data.name || data.hue_name,
      link: data.absoluteUrl || data.link,
      description: data.description || data.hue_description,
      isDirectory: data.doc_type === 'directory' || data.type === 'directory',
      definition: ko.observable({
        type: data.doc_type || data.type
      })
    };
    self.data = data;
    self.loading = ko.observable(true);
    self.hasErrors = ko.observable(false);
    self.errorText = ko.observable();
    self.template = TEMPLATE_NAME;

    self.documentId = ko.observable();
    self.documentContents = ko.observable();
    self.loadDocument();

    const showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', () => {
      huePubSub.publish(ASSIST_DOC_HIGHLIGHT_EVENT, {
        parentUuid: self.data.parentUuid,
        docUuid: self.data.uuid
      });
    });

    self.disposals.push(() => {
      showInAssistPubSub.remove();
    });
  }

  download() {
    if (this.documentId()) {
      window.location.href = `${
        window.HUE_BASE_URL
      }/desktop/api2/doc/export?documents=[${this.documentId()}]`;
    }
  }

  open(entry) {
    huePubSub.publish('open.link', entry.details.link);
    huePubSub.publish('context.popover.hide');
    huePubSub.publish('global.search.close');
  }

  dispose() {
    const self = this;
    while (self.disposals.length) {
      self.disposals.pop()();
    }
  }

  loadDocument() {
    const self = this;
    self.hasErrors(false);
    self.loading(true);
    apiHelper
      .fetchDocument({
        uuid: self.data.uuid,
        fetchContents: true,
        silenceErrors: true
      })
      .done(response => {
        this.documentId(response.document?.id);
        self.documentContents(response.data);
        self.loading(false);
      })
      .fail(() => {
        self.loading(false);
        self.hasErrors(false); // Allows us to revert to a generic document panel in case it can't fetch it.
      });
  }
}

export default DocumentContext;
