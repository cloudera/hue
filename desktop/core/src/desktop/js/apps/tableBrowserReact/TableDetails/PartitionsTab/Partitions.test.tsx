// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import Partitions from './Partitions';

jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock CUIX components to avoid styled-components
jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));
jest.mock('cuix/dist/components/Button', () => ({
  __esModule: true,
  BorderlessButton: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
}));
jest.mock('cuix/dist/components/Tooltip', () => ({
  __esModule: true,
  default: ({ children }: any) => <span>{children}</span>
}));
jest.mock('cuix/dist/components/Modal', () => ({
  __esModule: true,
  default: ({ open, title, onOk, onCancel, children }: any) => (
    <div data-testid="modal" hidden={!open}>
      <div>{title}</div>
      <div>{children}</div>
      <button onClick={onOk}>OK</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  )
}));
jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title, subtitle }: any) => (
    <div>
      <div>{title}</div>
      <div>{subtitle}</div>
    </div>
  )
}));
jest.mock('cuix/dist/components/Button/Button', () => ({
  __esModule: true,
  default: ({ children, onClick, disabled }: any) => (
    <button onClick={onClick} disabled={disabled}>
      {children}
    </button>
  )
}));
jest.mock('antd', () => ({
  __esModule: true,
  ConfigProvider: ({ children }: any) => <>{children}</>
}));

// Mock Filter with triggers
jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (out: Record<string, unknown[]>) => void }) => (
    <div>
      <button aria-label="facet-country-us" onClick={() => onChange({ country: ['US'] })} />
      <button aria-label="search-2020" onClick={() => onChange({ search: ['2020'] })} />
      <button aria-label="clear" onClick={() => onChange({})} />
    </div>
  )
}));

// Mock PaginatedTable to render rows and allow selecting
jest.mock('../../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({ data, onRowSelect }: { data: Array<{ key: string }>; onRowSelect?: (r: any[]) => void }) => (
    <div>
      <div data-testid="rows">
        {data.map(r => (
          <div key={r.key}>{r.key}</div>
        ))}
      </div>
      {onRowSelect && (
        <button aria-label="select-first" onClick={() => onRowSelect([data[0]])} />
      )}
    </div>
  )
}));

// Mock dataCatalog
jest.mock('../../../../catalog/dataCatalog', () => ({
  __esModule: true,
  default: {
    getEntry: jest.fn().mockImplementation(async () => ({
      getAnalysis: jest.fn().mockResolvedValue({
        partition_keys: [{ name: 'country' }]
      }),
      getPartitions: jest.fn().mockResolvedValue({
        partition_keys_json: ['country'],
        partition_values_json: [
          { partitionSpec: "country=US", columns: ['US'] },
          { partitionSpec: "country=SE", columns: ['SE'] }
        ]
      })
    }))
  }
}));

describe('Partitions', () => {
  const connector = { id: 'hive', type: 'hive', dialect: 'hive' } as unknown as any;
  const namespace = { id: 'ns' } as unknown as any;
  const compute = { id: 'cm' } as unknown as any;

  it('renders rows and filters with facet + search', async () => {
    const user = userEvent.setup();
    render(
      <Partitions
        connector={connector}
        namespace={namespace}
        compute={compute}
        database="default"
        table="customers"
      />
    );

    // There are two tables with data-testid="rows": keys and values. Values should have two rows.
    const allRows = await screen.findAllByTestId('rows');
    const valueRows = allRows[1];
    expect(valueRows.children.length).toBe(2);

    // Apply facet filter -> only US
    await user.click(screen.getByLabelText('facet-country-us'));
    expect(valueRows.children.length).toBe(1);

    // Clear -> back to two
    await user.click(screen.getByLabelText('clear'));
    expect(valueRows.children.length).toBe(2);
  });

  it('enables drop button on selection and opens confirm modal', async () => {
    const user = userEvent.setup();
    render(
      <Partitions
        connector={connector}
        namespace={namespace}
        compute={compute}
        database="default"
        table="customers"
      />
    );

    // Drop button disabled initially
    const dropBtn = await screen.findByRole('button', { name: 'Drop partition(s)' });
    expect(dropBtn).toBeDisabled();

    // Select first row
    await user.click(screen.getByLabelText('select-first'));
    expect(dropBtn).not.toBeDisabled();

    // Open confirm
    await user.click(dropBtn);
    const modal = screen.getAllByTestId('modal').find(m => !m.hasAttribute('hidden'))!;
    expect(modal).toBeInTheDocument();
  });
});


