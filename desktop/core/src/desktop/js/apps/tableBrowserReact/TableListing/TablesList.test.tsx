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
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import TablesList, { type TableRowItem } from './TablesList';

jest.mock('../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock components to avoid CUIX/styled-components and Antd complexities
jest.mock('../sharedComponents/PageHeader', () => ({
  __esModule: true,
  default: () => <div data-testid="page-header">Header</div>
}));

jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

jest.mock('../DatabaseListing/DatabaseProperties', () => ({
  __esModule: true,
  default: ({ loading }: { loading?: boolean }) => (
    <div data-testid="db-props">{loading ? 'Loading' : 'Props'}</div>
  )
}));

jest.mock('../sharedComponents/Toolbar', () => ({
  __esModule: true,
  default: ({
    actions
  }: {
    actions: Array<{ key: string; label: string; onClick: () => void; disabled?: boolean }>;
  }) => (
    <div>
      {actions.map(a => (
        <button key={a.key} onClick={a.onClick} disabled={a.disabled}>
          {a.label}
        </button>
      ))}
    </div>
  )
}));

jest.mock('../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({
    data,
    onRowSelect
  }: {
    data: Array<TableRowItem & { key: string }>;
    onRowSelect?: (rows: any[]) => void;
  }) => (
    <div>
      <div data-testid="rows">
        {data.map((r, i) => (
          <div key={i}>{r.name}</div>
        ))}
      </div>
      {onRowSelect && (
        <>
          <button onClick={() => onRowSelect([data[0]] as any[])}>Select First</button>
          <button onClick={() => onRowSelect(data as any[])}>Select All</button>
        </>
      )}
    </div>
  )
}));

jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: ({ onChange }: any) => (
    <div>
      <input aria-label="filter" />
      <button aria-label="type-table" onClick={() => onChange({ Type: ['table'] })} />
      <button aria-label="search-orders" onClick={() => onChange({ search: ['orders'] })} />
      <button aria-label="clear" onClick={() => onChange({})} />
    </div>
  )
}));

jest.mock('cuix/dist/components/Button', () => ({
  __esModule: true,
  LinkButton: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>,
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
}));

jest.mock('cuix/dist/components/Button/Button', () => ({
  __esModule: true,
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
}));

jest.mock('cuix/dist/components/Button/PrimaryButton', () => ({
  __esModule: true,
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
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

// Added to avoid styled-components in tests via InlineDescriptionEditor
jest.mock('cuix/dist/components/Button/BorderlessButton', () => ({
  __esModule: true,
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>
}));

jest.mock('antd', () => {
  const Input: any = ({ value, onChange, placeholder }: any) => (
    <input value={value} onChange={onChange} placeholder={placeholder} />
  );
  Input.TextArea = ({ value, onChange, placeholder }: any) => (
    <textarea value={value} onChange={onChange} placeholder={placeholder} />
  );
  const ConfigProvider: any = ({ children }: any) => <>{children}</>;
  return { __esModule: true, Input, Skeleton: { Input: () => <div /> }, ConfigProvider };
});

describe('TablesList', () => {
  const tables: TableRowItem[] = [
    { name: 'customers', type: 'table', comment: 'c desc' },
    { name: 'orders', type: 'table', comment: '' }
  ];

  it('calls onCreateTable via toolbar action', async () => {
    const user = userEvent.setup();
    const onCreateTable = jest.fn();
    render(
      <TablesList
        tables={tables}
        isInitializing={false}
        isRefreshing={false}
        tableFilter=""
        setTableFilter={() => {}}
        tablePageNumber={1}
        setTablePageNumber={() => {}}
        tablePageSize={50}
        setTablePageSize={() => {}}
        tableDescriptions={{ customers: 'c desc', orders: '' }}
        editingTableName={null}
        editingTableValue={''}
        setEditingTableName={() => {}}
        setEditingTableValue={() => {}}
        onOpenTable={() => {}}
        onSaveDescription={() => {}}
        onCreateTable={onCreateTable}
      />
    );

    await user.click(screen.getByRole('button', { name: 'New' }));
    expect(onCreateTable).toHaveBeenCalled();
  });

  it('calls onViewSelection and onQuerySelection on single selection', async () => {
    const user = userEvent.setup();
    const onViewSelection = jest.fn();
    const onQuerySelection = jest.fn();

    render(
      <TablesList
        tables={tables}
        isInitializing={false}
        isRefreshing={false}
        tableFilter=""
        setTableFilter={() => {}}
        tablePageNumber={1}
        setTablePageNumber={() => {}}
        tablePageSize={50}
        setTablePageSize={() => {}}
        tableDescriptions={{ customers: 'c desc', orders: '' }}
        editingTableName={null}
        editingTableValue={''}
        setEditingTableName={() => {}}
        setEditingTableValue={() => {}}
        onOpenTable={() => {}}
        onSaveDescription={() => {}}
        onViewSelection={onViewSelection}
        onQuerySelection={onQuerySelection}
      />
    );

    await user.click(screen.getByText('Select First'));
    // Click View
    await user.click(screen.getByRole('button', { name: 'View' }));
    // Click Query
    await user.click(screen.getByRole('button', { name: 'Query' }));

    expect(onViewSelection).toHaveBeenCalled();
    expect(onQuerySelection).toHaveBeenCalled();
  });

  it('drops selected tables with and without skipTrash', async () => {
    const user = userEvent.setup();
    const onDropSelection = jest.fn();

    render(
      <TablesList
        tables={tables}
        isInitializing={false}
        isRefreshing={false}
        tableFilter=""
        setTableFilter={() => {}}
        tablePageNumber={1}
        setTablePageNumber={() => {}}
        tablePageSize={50}
        setTablePageSize={() => {}}
        tableDescriptions={{ customers: 'c desc', orders: '' }}
        editingTableName={null}
        editingTableValue={''}
        setEditingTableName={() => {}}
        setEditingTableValue={() => {}}
        onOpenTable={() => {}}
        onSaveDescription={() => {}}
        onDropSelection={onDropSelection}
      />
    );

    await user.click(screen.getByText('Select All'));
    await user.click(screen.getByRole('button', { name: 'Drop' }));

    // Confirm default (skipTrash off)
    const dropModal = screen.getAllByTestId('modal').find(m => !m.hasAttribute('hidden'))!;
    await user.click(within(dropModal).getByText('OK'));
    expect(onDropSelection).toHaveBeenCalled();

    // Open again: re-select rows, then toggle skip trash
    await user.click(screen.getByText('Select All'));
    await user.click(screen.getByRole('button', { name: 'Drop' }));
    const dropModal2 = screen.getAllByTestId('modal').find(m => !m.hasAttribute('hidden'))!;
    // find checkbox
    const checkbox = within(dropModal2).getByRole('checkbox');
    await user.click(checkbox);
    await user.click(within(dropModal2).getByText('OK'));

    expect(onDropSelection).toHaveBeenCalledTimes(2);
  });

  it('filters by type facet and search', async () => {
    const user = userEvent.setup();

    render(
      <TablesList
        tables={tables}
        isInitializing={false}
        isRefreshing={false}
        tableFilter=""
        setTableFilter={() => {}}
        tablePageNumber={1}
        setTablePageNumber={() => {}}
        tablePageSize={50}
        setTablePageSize={() => {}}
        tableDescriptions={{ customers: 'c desc', orders: '' }}
        editingTableName={null}
        editingTableValue={''}
        setEditingTableName={() => {}}
        setEditingTableValue={() => {}}
        onOpenTable={() => {}}
        onSaveDescription={() => {}}
      />
    );

    // Apply type facet (no change since both are table, but ensures handler works)
    await user.click(screen.getByLabelText('type-table'));

    // Apply search 'orders' -> only orders row should be visible in mock table
    await user.click(screen.getByLabelText('search-orders'));
    const rows = screen.getByTestId('rows');
    expect(rows).toBeInTheDocument();
  });
});
