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

jest.useFakeTimers();

// Mock Hue pub/sub to capture publishes
jest.mock('utils/huePubSub', () => {
  return {
    publish: jest.fn(),
    subscribe: jest.fn(() => ({ remove: jest.fn() }))
  };
});

// Minimal mocks for location/gutter handlers
jest.mock('ko/bindings/ace/aceLocationHandler', () => {
  return {
    __esModule: true,
    default: jest.fn().mockImplementation(() => ({ dispose: jest.fn() })),
    REFRESH_STATEMENT_LOCATIONS_EVENT: 'ace.refresh.statement.locations'
  };
});

jest.mock('ko/bindings/ace/aceGutterHandler', () => {
  return jest.fn().mockImplementation(() => ({ dispose: jest.fn() }));
});

// Mock Ace helper with a minimal editor implementation
jest.mock('ext/aceHelper', () => {
  const editor = {
    session: {
      setMode: jest.fn(),
      getMode: jest.fn(() => ({ $id: '' })),
      getLength: jest.fn().mockReturnValue(1),
      getLine: jest.fn().mockReturnValue(''),
      getDocument: jest.fn(() => ({ replace: jest.fn() })),
      selection: { getRange: jest.fn(() => ({})) }
    },
    renderer: { scrollCursorIntoView: jest.fn(), scroller: {} },
    setOptions: jest.fn(),
    setOption: jest.fn(),
    getOption: jest.fn().mockReturnValue(false),
    setTheme: jest.fn(),
    addError: jest.fn(),
    addWarning: jest.fn(),
    clearErrorsAndWarnings: jest.fn(),
    scrollToLine: jest.fn(),
    getSelectedText: jest.fn().mockReturnValue(''),
    getValue: jest.fn().mockReturnValue(''),
    moveCursorToPosition: jest.fn(),
    centerSelection: jest.fn(),
    on: jest.fn(() => {}),
    off: jest.fn(() => {}),
    selection: { on: jest.fn(() => {}), off: jest.fn(() => {}) },
    commands: {
      addCommand: jest.fn(),
      on: jest.fn(() => {}),
      off: jest.fn(() => {}),
      commands: { gotoline: { exec: jest.fn() } },
      bindKey: jest.fn()
    },
    getTextBeforeCursor: jest.fn().mockReturnValue(''),
    removeTextBeforeCursor: jest.fn(),
    execCommand: jest.fn(),
    disableAutocomplete: jest.fn(),
    enableAutocomplete: jest.fn(),
    showFileButton: jest.fn(() => ({ on: jest.fn() })),
    hideFileButton: jest.fn(),
    focus: jest.fn()
  };

  const mockRequire = id => {
    if (id === 'ace/range') {
      return { Range: function () {} };
    }
    if (id === 'ace/autocomplete') {
      return { Autocomplete: function () {} };
    }
    if (id === 'ace/ext/language_tools') {
      return {
        textCompleter: { setSqlMode: jest.fn() },
        snippetCompleter: {},
        keyWordCompleter: {},
        setSqlMode: jest.fn()
      };
    }
    if (id === 'ace/lib/dom') {
      return { importCssString: jest.fn() };
    }
    return {};
  };

  return {
    __esModule: true,
    default: {
      edit: jest.fn(() => editor),
      require: mockRequire
    },
    edit: jest.fn(() => editor),
    require: mockRequire
  };
});

// Import the binding to register it
import './ko.aceEditor';
import huePubSub from 'utils/huePubSub';

describe('ko.aceEditor binding', () => {
  it('publishes editor.ready once after Ace initialization', () => {
    document.body.innerHTML = '<div id="editor-1"></div>';
    const el = document.getElementById('editor-1');
    // Attach jQuery data to mirror runtime usage
    $(el).data('last-active-editor', false);

    // Prevent setInterval loop inside binding from scheduling real timers
    jest.spyOn(global, 'setInterval').mockImplementation(() => 1);

    const snippet = {
      id: () => 'editor-1',
      statement_raw: ko.observable(''),
      getAceMode: () => 'ace/mode/sql',
      isSqlDialect: () => true,
      aceCursorPosition: () => null,
      aceErrors: ko.pureComputed(() => []),
      aceWarnings: ko.pureComputed(() => []),
      errors: ko.observableArray([]),
      inFocus: ko.observable(false),
      executor: {},
      lastAceSelectionRowOffset: () => 0,
      getPlaceHolder: () => ''
    };
    let aceRef = null;
    // v1 style accessor/setter
    snippet.ace = newVal => {
      if (newVal) {
        aceRef = newVal;
      }
      return aceRef;
    };

    // Apply binding directly to the element
    el.setAttribute('data-bind', 'aceEditor: { snippet: snippet }');
    const vm = { snippet };
    ko.applyBindings(vm, el);

    expect(huePubSub.publish).not.toHaveBeenCalledWith('editor.ready');

    // Flush the zero-timeout publish without executing intervals
    jest.runOnlyPendingTimers();

    expect(huePubSub.publish).toHaveBeenCalledWith('editor.ready');

    // Ensure it only publishes once per element
    const publishCount = huePubSub.publish.mock.calls.filter(
      call => call[0] === 'editor.ready'
    ).length;
    expect(publishCount).toBe(1);
  });
});


