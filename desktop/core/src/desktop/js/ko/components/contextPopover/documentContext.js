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

import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';

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
    self.template = 'context-document-details';

    self.documentContents = ko.observable();
    self.loadDocument();

    const showInAssistPubSub = huePubSub.subscribe('context.popover.show.in.assist', () => {
      huePubSub.publish('assist.doc.highlight', {
        parentUuid: self.data.parentUuid,
        docUuid: self.data.uuid
      });
    });

    self.disposals.push(() => {
      showInAssistPubSub.remove();
    });
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
