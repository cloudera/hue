// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import Schema, { type ColumnDef } from './Schema';

jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Avoid Tooltip styled/ESM imports
jest.mock('cuix/dist/components/Tooltip', () => ({
  __esModule: true,
  default: ({ children }: any) => <span>{children}</span>
}));

// Avoid styled-components in tests
jest.mock('cuix/dist/components/Button/BorderlessButton', () => ({
  __esModule: true,
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
}));

// Mock Filter: expose controls to trigger onChange with search and facets
jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (out: Record<string, unknown[]>) => void }) => (
    <div>
      <button
        onClick={() => onChange({ search: ['cust'] } as unknown as Record<string, unknown[]>)}
      >
        set-search-cust
      </button>
      <button onClick={() => onChange({} as unknown as Record<string, unknown[]>)}>clear</button>
      <button onClick={() => onChange({ Type: ['int'] } as unknown as Record<string, unknown[]>)}>
        facet-type-int
      </button>
      <button
        onClick={() =>
          onChange({ 'Partition key': ['Yes'] } as unknown as Record<string, unknown[]>)
        }
      >
        facet-partition-yes
      </button>
      <button
        onClick={() =>
          onChange({ 'Partition key': ['No'] } as unknown as Record<string, unknown[]>)
        }
      >
        facet-partition-no
      </button>
    </div>
  )
}));

// Mock PaginatedTable to render row names for count assertions
jest.mock('../../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({ data }: { data: Array<ColumnDef & { key: string }> }) => (
    <div data-testid="rows">
      {data.map(r => (
        <div key={r.key}>{r.name}</div>
      ))}
    </div>
  )
}));

describe('Schema filters', () => {
  const columns: ColumnDef[] = [
    { name: 'customer_id', type: 'int', comment: 'id', isPartitionKey: true },
    { name: 'customer_name', type: 'string', comment: 'name' },
    { name: 'order_total', type: 'decimal(10,2)', comment: 'amount' }
  ];

  it('filters by search text', async () => {
    const user = userEvent.setup();
    const onCountChange = jest.fn();
    render(<Schema columns={columns} onOpenColumn={() => {}} onCountChange={onCountChange} />);

    // Initial count called
    expect(onCountChange).toHaveBeenLastCalledWith(3);

    // Apply search 'cust'
    await user.click(screen.getByText('set-search-cust'));
    expect(onCountChange).toHaveBeenLastCalledWith(2);
    expect(screen.getAllByTestId('rows')[0].children.length).toBeGreaterThan(0);

    // Clear
    await user.click(screen.getByText('clear'));
    expect(onCountChange).toHaveBeenLastCalledWith(3);
  });

  it('filters by Type facet', async () => {
    const user = userEvent.setup();
    const onCountChange = jest.fn();
    render(<Schema columns={columns} onCountChange={onCountChange} />);
    expect(onCountChange).toHaveBeenLastCalledWith(3);
    await user.click(screen.getByText('facet-type-int'));
    expect(onCountChange).toHaveBeenLastCalledWith(1);
  });

  it('filters by Partition key facet', async () => {
    const user = userEvent.setup();
    const onCountChange = jest.fn();
    render(<Schema columns={columns} onCountChange={onCountChange} />);
    expect(onCountChange).toHaveBeenLastCalledWith(3);
    await user.click(screen.getByText('facet-partition-yes'));
    expect(onCountChange).toHaveBeenLastCalledWith(1);
    await user.click(screen.getByText('facet-partition-no'));
    // Only No selected (last call) -> 2
    expect(onCountChange).toHaveBeenLastCalledWith(2);
  });
});
