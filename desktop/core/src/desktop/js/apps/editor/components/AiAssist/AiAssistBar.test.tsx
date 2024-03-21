/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import React from 'react';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import Executor from '../../execution/executor';
import SqlExecutable from '../../execution/sqlExecutable';

import AiAssistBar from './AiAssistBar';

import * as hooks from './hooks';

jest.mock('../../../../config/hueConfig', () => {
  // We need to import the AiActionModes here since Jest mocks
  // arent allowed to access variables outside of the module
  const { AiActionModes } = require('./sharedTypes'); 
  return {
    getLastKnownConfig: jest.fn().mockReturnValue({
      hue_config: {
        ai_enabled_SQL_tasks: Object.values(AiActionModes),
      },
    }),
  };
});

jest.spyOn(hooks, 'useKeywordCase').mockReturnValue('upper');
jest.spyOn(hooks, 'useResizeAwareElementSize').mockReturnValue({ height: 100, width: 100 });
jest.spyOn(hooks, 'useKeyboardShortcuts');
jest.spyOn(hooks, 'useLocalStorageHistory').mockReturnValue([[], jest.fn()]);

// Mock AiPreviewModal as an empty component
jest.mock('./PreviewModal/AiPreviewModal', () => {
  return {
    // This property makes it work as a module
    __esModule: true,
    default: jest.fn(
      ({
        onCancel,
        onInsert,
        suggestion,
        nql,
        assumptions,
        explanation,
        summary,
        showDiffFrom
      }) => {
        return (
          // Mock the actions interacting with the AiAssistBar
          <div data-testid="mock-preview-modal">
            {nql}
            {suggestion}
            {assumptions}
            {explanation}
            {summary}
            {showDiffFrom}

            <button type="button" onClick={() => onInsert(suggestion)}>
              Insert
            </button>
            <button type="button" onClick={onCancel}>
              Cancel
            </button>
          </div>
        );
      }
    )
  };
});

// Mock lodash throttle
jest.mock('lodash', () => ({
  throttle: jest.fn(fn => fn)
}));

// Mock huePubSub
jest.mock('utils/huePubSub', () => ({
  subscribe: jest.fn(() => ({
    remove: jest.fn()
  })),
  publish: jest.fn(() => ({
    remove: jest.fn()
  }))
}));

// Mock storageUtils
jest.mock('utils/storageUtils', () => ({
  getFromLocalStorage: jest.fn(),
  setInLocalStorage: jest.fn()
}));

// By mocking the generativeFunctionFactory we don't need to mock
// the actual implementation of the API calls
jest.mock('api/apiAIHelper', () => ({
  generativeFunctionFactory: jest.fn(() => ({
    generateExplanation: jest.fn().mockResolvedValue({
      explain: 'Mock explanation',
      summary: 'Mock summary'
    }),
    generateCorrectedSql: jest.fn().mockResolvedValue('Mock corrected SQL'),
    generateOptimizedSql: jest.fn().mockResolvedValue({
      sql: 'Mock optimized SQL',
      explain: 'Mock optimization explanation'
    }),
    generateSQLfromNQL: jest.fn().mockResolvedValue({
      sql: 'Mock generated SQL from NQL',
      assumptions: 'Mock generate assumptions'
    }),
    generateEditedSQLfromNQL: jest.fn().mockResolvedValue({
      sql: 'Mock edited SQL from NQL',
      assumptions: 'Mock edited assumptions'
    })
  }))
}));

describe('AiAssistBar', () => {
  const mockExecutor = (mock: unknown): Executor => mock as Executor;
  let sqlExecutableMock: SqlExecutable;

  beforeEach(() => {
    sqlExecutableMock = new SqlExecutable({
      database: 'default',
      parsedStatement: { statement: 'select * from test' },
      executor: mockExecutor({
        connector: () => ({ id: 'test', dialect: 'hive' }),
        compute: () => ({ id: 'test' }),
        namespace: () => ({ id: 'test' }),
        defaultLimit: () => 100,
        toJs: () => ({})
      })
    });
  });

  it('renders the AI assist bar with toolbar', async () => {
    const { getByTestId } = render(<AiAssistBar activeExecutable={sqlExecutableMock} />);
    expect(getByTestId('hue-ai-assist-toolbar')).toBeInTheDocument();
  });

  it('clears nql, sql & assumptions state after cancelling a preview modal', async () => {
    const user = userEvent.setup();
    const { getByTestId, getByRole, getByTitle, queryByTestId } = render(
      <AiAssistBar activeExecutable={sqlExecutableMock} />
    );

    expect(queryByTestId('mock-preview-modal')).toBeNull();

    await user.click(getByRole('button', { name: 'Generate SQL using natural language' }));
    const inputField = getByTitle('Press down arrow to select from history');
    expect(inputField).toBeInTheDocument();

    await user.type(inputField, 'test prompt input');
    await user.click(getByRole('button', { name: 'Press enter or click here to execute' }));

    expect(getByTestId('mock-preview-modal')).toBeInTheDocument();
    expect(getByTestId('mock-preview-modal')).toHaveTextContent('test prompt input');
    expect(getByTestId('mock-preview-modal')).toHaveTextContent('Mock generated SQL from NQL');
    expect(getByTestId('mock-preview-modal')).toHaveTextContent('Mock generate assumptions');

    await user.click(getByRole('button', { name: 'Cancel' }));
    expect(queryByTestId('mock-preview-modal')).toBeNull();

    await user.click(getByRole('button', { name: 'Explain SQL statement' }));
    expect(getByTestId('mock-preview-modal')).toBeInTheDocument();
    expect(getByTestId('mock-preview-modal')).not.toHaveTextContent('test prompt input');
    expect(getByTestId('mock-preview-modal')).not.toHaveTextContent('Mock generated SQL from NQL');
    expect(getByTestId('mock-preview-modal')).not.toHaveTextContent('Mock generate assumptions');
  });

  it('adds both original and modified SQL to preview modal for Edit', async () => {
    const user = userEvent.setup();
    const { getByTestId, getByRole, getByTitle } = render(
      <AiAssistBar activeExecutable={sqlExecutableMock} />
    );

    await user.click(getByRole('button', { name: 'Edit SQL using natural language' }));
    const inputField = getByTitle('Press down arrow to select from history');
    expect(inputField).toBeInTheDocument();

    await user.type(inputField, 'test prompt input');
    await user.click(getByRole('button', { name: 'Press enter or click here to execute' }));

    expect(getByTestId('mock-preview-modal')).toBeInTheDocument();
    expect(getByTestId('mock-preview-modal')).toHaveTextContent('select * from test');
    expect(getByTestId('mock-preview-modal')).toHaveTextContent('Mock edited SQL from NQL');
  });
});
