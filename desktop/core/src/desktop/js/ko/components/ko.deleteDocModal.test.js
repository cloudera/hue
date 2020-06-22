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
import { DELETE_DOC_MODAL_SHOWN_EVENT, SHOW_DELETE_DOC_MODAL_EVENT } from './ko.deleteDocModal';
import huePubSub from 'utils/huePubSub';

describe('ko.deleteDocModal.js', () => {
  it('should render component', async () => {
    huePubSub.publish(SHOW_DELETE_DOC_MODAL_EVENT, {
      entriesToDelete: ko.observableArray(),
      selectedEntries: ko.observableArray([{ selected: ko.observable(true) }]),
      sharedWithMeSelected: ko.observable(false),
      selectedDocsWithDependents: ko.observableArray(),
      deletingEntries: ko.observable(false),
      getSelectedDocsWithDependents: () => {}
    });

    await new Promise(resolve => {
      huePubSub.subscribeOnce(DELETE_DOC_MODAL_SHOWN_EVENT, resolve);
    });

    expect(window.document.documentElement.outerHTML).toMatchSnapshot();
  });
});
