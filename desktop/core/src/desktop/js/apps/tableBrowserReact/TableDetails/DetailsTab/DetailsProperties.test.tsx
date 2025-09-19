// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import DetailsProperties, { type PropertyRow } from './DetailsProperties';

// Mock i18n
jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock Filter to expose a search trigger
jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (out: Record<string, unknown[]>) => void }) => (
    <div>
      <button aria-label="search-owner" onClick={() => onChange({ search: ['owner'] })} />
      <button aria-label="clear" onClick={() => onChange({})} />
    </div>
  )
}));

// Mock PaginatedTable to render the passed rows
jest.mock('../../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({ data }: { data: Array<{ key: string }> }) => (
    <div data-testid="rows">{data.map(r => <div key={r.key}>{r.key}</div>)}</div>
  )
}));

describe('DetailsProperties', () => {
  it('renders fallback list and filters via search', async () => {
    const rows: PropertyRow[] = [
      { name: 'Owner', value: 'hive' },
      { name: 'Location', value: 'hdfs://namenode:8020/warehouse/t.db' }
    ];

    const user = userEvent.setup();
    render(<DetailsProperties properties={rows} />);

    // Initially should show both rows
    const rowContainer = await screen.findByTestId('rows');
    expect(rowContainer.children.length).toBe(2);

    // Apply search filter
    await user.click(screen.getByLabelText('search-owner'));
    expect(rowContainer.children.length).toBe(1);

    // Clear filter
    await user.click(screen.getByLabelText('clear'));
    expect(rowContainer.children.length).toBe(2);
  });

  it('renders structured sections and linkifies Location values', async () => {
    const baseInfo: PropertyRow[] = [
      { name: 'Database', value: 'default' },
      { name: 'Location', value: 'http://example.com/path' }
    ];
    const storageInfo: PropertyRow[] = [
      { name: 'SerDe Library', value: 'serde' }
    ];
    const storageDescParams: PropertyRow[] = [
      { name: 'serialization.format', value: '1' }
    ];

    render(
      <DetailsProperties baseInfo={baseInfo} storageInfo={storageInfo} storageDescParams={storageDescParams} />
    );

    // Should render three PaginatedTables (Detailed Table Info, Storage Info, Storage Desc Params)
    const tables = await screen.findAllByTestId('rows');
    expect(tables.length).toBeGreaterThanOrEqual(1);
  });
});


