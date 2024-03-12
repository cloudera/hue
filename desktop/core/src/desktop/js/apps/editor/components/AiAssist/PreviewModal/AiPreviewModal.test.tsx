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
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PreviewModal from './AiPreviewModal';
import { AiActionModes } from '../sharedTypes';

describe('PreviewModal', () => {
  const commonProps = {
    open: true,
    suggestion: 'SELECT * FROM table;',
    assumptions: '',
    explanation: '',
    summary: '',
    onCancel: jest.fn(),
    onInsert: jest.fn(),
    primaryButtonLabel: 'Run',
    showDiffFrom: '',
    lineNumberStart: 1,
    dialect: 'hive',
    keywordCase: undefined
  };

  test.each([
    [AiActionModes.GENERATE, 'Generated SQL - suggestion'],
    [AiActionModes.EDIT, 'Edited SQL - suggestion'],
    [AiActionModes.OPTIMIZE, 'Optimized SQL - suggestion'],
    [AiActionModes.EXPLAIN, 'Explained SQL'],
    [AiActionModes.FIX, 'Fixed SQL - suggestion']
  ])('displays the correct title for %s action mode with diff', (actionMode, expectedTitle) => {
    render(
      <PreviewModal
        {...commonProps}
        actionMode={actionMode}
        showDiffFrom="SELECT * FROM old_table;"
      />
    );
    expect(screen.getByRole('dialog')).toHaveTextContent(expectedTitle);
  });

  test.each([
    [AiActionModes.OPTIMIZE, 'Optimized SQL - no suggestion'],
    [AiActionModes.EDIT, 'Edited SQL - no suggestion'],
    [AiActionModes.FIX, 'Fixed SQL - no suggestion']
  ])('displays the correct title for %s action mode without diff', (actionMode, expectedTitle) => {
    render(
      <PreviewModal
        {...commonProps}
        actionMode={actionMode}
        showDiffFrom={commonProps.suggestion}
      />
    );
    expect(screen.getByRole('dialog')).toHaveTextContent(expectedTitle);
  });

  test.each([
    [AiActionModes.OPTIMIZE, 'No optimization to the SQL statement could be suggested.'],
    [AiActionModes.FIX, 'Fixed SQL - no suggestion'],
    [
      AiActionModes.EDIT,
      'The SQL statement could not be edited based on the input given. The AI has returned an unmodified SQL statement.'
    ]
  ])('displays the correct message for %s action mode without diff', (actionMode, expectedMsg) => {
    render(
      <PreviewModal
        {...commonProps}
        actionMode={actionMode}
        showDiffFrom={commonProps.suggestion}
      />
    );
    expect(screen.getByRole('dialog')).toHaveTextContent(expectedMsg);
  });
});
