// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { shallowMount } from '@vue/test-utils';
import { CancellablePromise } from 'api/cancellablePromise';
import Executor from 'apps/editor/execution/executor';
import dataCatalog from 'catalog/dataCatalog';
import { Ace } from 'ext/ace';
import { INSERT_AT_CURSOR_EVENT } from 'ko/bindings/ace/ko.aceEditor';
import huePubSub from 'utils/huePubSub';
import { nextTick } from 'vue';
import AceEditor from './AceEditor.vue';

describe('AceEditor.vue', () => {
  const mockExecutor = ({
    connector: ko.observable({
      dialect: 'foo',
      id: 'foo'
    }),
    namespace: ko.observable({
      id: 'foo'
    }),
    compute: ko.observable({
      id: 'foo'
    })
  } as unknown) as Executor;

  it('should render', () => {
    spyOn(dataCatalog, 'getChildren').and.returnValue(CancellablePromise.resolve([]));

    const wrapper = shallowMount(AceEditor, {
      props: {
        value: 'some query',
        id: 'some-id',
        executor: mockExecutor
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should handle drag and drop pubsub event targeting this editor', async () => {
    spyOn(dataCatalog, 'getChildren').and.returnValue(CancellablePromise.resolve([]));

    const wrapper = shallowMount(AceEditor, {
      props: {
        value: '',
        id: 'some-id',
        executor: mockExecutor
      }
    });

    await nextTick();

    expect(wrapper.emitted()['ace-created']).toBeTruthy();

    const editor = (wrapper.emitted()['ace-created'][0] as Ace.Editor[])[0];

    const draggedText = 'Some dropped text';
    huePubSub.publish(INSERT_AT_CURSOR_EVENT, {
      text: draggedText,
      targetEditor: editor,
      cursorEndAdjust: 0
    });

    expect(editor.getValue()).toEqual(draggedText);
  });

  it('should not handle drag and drop pubsub event targeting another editor', async () => {
    spyOn(dataCatalog, 'getChildren').and.returnValue(CancellablePromise.resolve([]));

    const wrapper = shallowMount(AceEditor, {
      props: {
        value: '',
        id: 'some-id',
        executor: mockExecutor
      }
    });

    await nextTick();

    expect(wrapper.emitted()['ace-created']).toBeTruthy();

    const editor = (wrapper.emitted()['ace-created'][0] as Ace.Editor[])[0];

    const draggedText = 'Some dropped text';
    huePubSub.publish(INSERT_AT_CURSOR_EVENT, {
      text: draggedText,
      targetEditor: {}, // Other instance
      cursorEndAdjust: 0
    });

    expect(editor.getValue()).not.toEqual(draggedText);
  });
});
