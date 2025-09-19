// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import ViewSql from './ViewSql';
import type { Analysis } from '../../../../catalog/DataCatalogEntry';

jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock CUIX components that may import non-JS assets (SVGs)
jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title, subtitle }: { title?: string; subtitle?: string }) => (
    <div data-testid="empty-state">
      <div>{title}</div>
      <div>{subtitle}</div>
    </div>
  )
}));
jest.mock('cuix/dist/components/Button', () => ({
  __esModule: true,
  default: ({ children, onClick, title }: any) => (
    <button onClick={onClick} title={title}>
      {children}
    </button>
  ),
  PrimaryButton: ({ children, onClick, title }: any) => (
    <button onClick={onClick} title={title}>
      {children}
    </button>
  )
}));

jest.mock('../../../../utils/huePubSub', () => ({
  __esModule: true,
  default: { publish: jest.fn() }
}));

const makeAnalysis = (
  props: Array<{ col_name: string; data_type?: string; comment?: string }>
): Analysis => ({
  // @ts-expect-error minimal shape for test
  properties: props
});

describe('ViewSql', () => {
  it('shows empty state when no SQL is available', () => {
    render(<ViewSql rawAnalysis={makeAnalysis([])} sourceType="hive" />);
    expect(screen.getByText(/No view SQL available/i)).toBeInTheDocument();
  });

  it('stitches multi-line SQL from properties and enables actions', async () => {
    const user = userEvent.setup();
    const props = [
      { col_name: 'View Original Text:', data_type: 'SELECT * FROM db.tbl WHERE a=1' },
      { col_name: '', data_type: 'AND b = 2' },
      { col_name: '', comment: 'ORDER BY c' },
      { col_name: 'Other Section' }
    ];

    render(<ViewSql rawAnalysis={makeAnalysis(props)} sourceType="impala" />);

    // Title and textarea should render
    expect(screen.getByText('View SQL')).toBeInTheDocument();
    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
    const value = textarea.value;
    // Allow basic formatter to insert newlines between clauses
    expect(value).toContain('SELECT *');
    expect(value).toContain('FROM db.tbl');
    expect(value).toContain('AND b = 2');
    expect(value).toContain('ORDER BY c');

    // Copy button should exist
    expect(screen.getByRole('button', { name: /Copy/i })).toBeInTheDocument();
    // Query button should exist
    expect(screen.getByRole('button', { name: /Query/i })).toBeInTheDocument();
  });
});
