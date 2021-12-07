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
import { AutocompleteParser, SqlParserProvider, SyntaxError, SyntaxParser } from 'parse/types';
import { SetOptions, SqlReferenceProvider, UdfCategory } from 'sql/reference/types';
import huePubSub from 'utils/huePubSub';
import AceEditor from './AceEditor.vue';

import impalaSyntaxParser from 'parse/sql/impala/impalaSyntaxParser';
import impalaAutocompleteParser from 'parse/sql/impala/impalaAutocompleteParser';

const sqlParserProvider: SqlParserProvider = {
  async getAutocompleteParser(): Promise<AutocompleteParser> {
    return impalaAutocompleteParser as unknown as AutocompleteParser;
  },

  async getSyntaxParser(): Promise<SyntaxParser> {
    return impalaSyntaxParser as unknown as SyntaxParser;
  }
};

const sqlReferenceProvider: SqlReferenceProvider = {
  getReservedKeywords(): Promise<Set<string>> {
    return Promise.resolve(new Set<string>());
  },
  getSetOptions(): Promise<SetOptions> {
    return Promise.resolve({});
  },
  getUdfCategories(): Promise<UdfCategory[]> {
    return Promise.resolve([]);
  },
  hasUdfCategories(): boolean {
    return false;
  }
};

describe('AceEditor.vue', () => {
  const mockExecutor = {
    connector: ko.observable({
      dialect: 'impala',
      id: 'impala'
    }),
    namespace: ko.observable({
      id: 'foo'
    }),
    compute: ko.observable({
      id: 'foo'
    }),
    database: ko.observable('default')
  } as unknown as Executor;

  let mountedTwice = false;

  const shallowMountForEditor = async (
    initialValue?: string
  ): Promise<{ element: Element; editor: Ace.Editor }> =>
    new Promise(resolve => {
      jest.spyOn(dataCatalog, 'getChildren').mockReturnValue(CancellablePromise.resolve([]));
      const props = {
        initialValue,
        id: 'some-id',
        executor: mockExecutor,
        sqlParserProvider,
        sqlReferenceProvider
      };

      let wrapper = shallowMount(AceEditor, { props });

      if (!mountedTwice) {
        // There seems to be a bug in vue-test-utils where the first mount won't trigger the onMounted hook.
        mountedTwice = true;
        wrapper = shallowMount(AceEditor, { props });
      }

      wrapper.vm.$nextTick(() => {
        expect(wrapper.emitted()['ace-created']).toBeTruthy();
        const editor = (wrapper.emitted()['ace-created'][0] as Ace.Editor[])[0];
        resolve({ element: wrapper.element, editor });
      });
    });

  it('should render', async () => {
    const { element } = await shallowMountForEditor('some query');
    expect(element).toMatchSnapshot();
  });

  it('should handle drag and drop pubsub event targeting this editor', async () => {
    const { editor } = await shallowMountForEditor();

    const draggedText = 'Some dropped text';
    huePubSub.publish(INSERT_AT_CURSOR_EVENT, {
      text: draggedText,
      targetEditor: editor,
      cursorEndAdjust: 0
    });

    expect(editor.getValue()).toEqual(draggedText);
  });

  it('should not handle drag and drop pubsub event targeting another editor', async () => {
    const { editor } = await shallowMountForEditor();

    const draggedText = 'Some dropped text';
    huePubSub.publish(INSERT_AT_CURSOR_EVENT, {
      text: draggedText,
      targetEditor: {}, // Other instance
      cursorEndAdjust: 0
    });

    expect(editor.getValue()).not.toEqual(draggedText);
  });

  it('should adjust parser 1-based parser location to 0-based ace range for syntax errors', async () => {
    const invalidTokenValue = 'slelect';
    const { editor } = await shallowMountForEditor(invalidTokenValue);
    expect(editor.getValue()).toEqual(invalidTokenValue);

    // Add syntax error manually (normally through web socket)
    const token = editor.session.getTokenAt(0, 0);
    expect(token).toBeDefined();
    expect(token!.value).toEqual(invalidTokenValue);
    const syntaxError: SyntaxError = {
      expected: [{ text: 'select', distance: 0 }],
      loc: { first_line: 1, last_line: 1, first_column: 0, last_column: 7 },
      text: invalidTokenValue
    };
    token!.syntaxError = syntaxError;

    // Listen for the dropdown show event
    let syntaxDropdownCalled = false;
    const subscription = huePubSub.subscribe('sql.syntax.dropdown.show', details => {
      expect(details.range.start.row).toEqual(syntaxError.loc.first_line - 1);
      expect(details.range.end.row).toEqual(syntaxError.loc.last_line - 1);
      expect(details.data).toEqual(syntaxError);
      syntaxDropdownCalled = true;
    });

    // Trigger right click in the editor
    editor.container.dispatchEvent(new MouseEvent('contextmenu', { clientX: 1, clientY: 1 }));
    subscription.remove();

    expect(syntaxDropdownCalled).toBeTruthy();
  });
});
