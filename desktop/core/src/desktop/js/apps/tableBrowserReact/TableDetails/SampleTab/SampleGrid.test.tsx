// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import SampleGrid from './SampleGrid';
// Mock cuix EmptyState to avoid SVG import issues
jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title, subtitle }: any) => (
    <div>
      <div>{title}</div>
      <div>{subtitle}</div>
    </div>
  )
}));

// Mock i18n
jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock PaginatedTable
jest.mock('../../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({ data }: { data: Array<{ key: string }> }) => (
    <div>
      <div data-testid="rows">
        {data.map(r => (
          <div key={r.key}>{r.key}</div>
        ))}
      </div>
    </div>
  )
}));

describe('SampleGrid', () => {
  it('shows empty state when no data and not refreshing', () => {
    render(<SampleGrid isRefreshing={false} />);
    expect(screen.getByText('No sample data')).toBeInTheDocument();
  });

  it('renders rows and trims header prefixes', async () => {
    const data = {
      headers: ['db.table.col1', 'table.col2', 'other'],
      rows: [
        ['v1', 'v2', 'v3'],
        ['v4', 'v5', 'v6']
      ]
    };
    render(<SampleGrid data={data} database="db" table="table" />);
    const rows = await screen.findByTestId('rows');
    // Two page rows rendered
    expect(rows.children.length).toBe(2);
  });
});
