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

import DatabasesList from './DatabasesList';

// Lightweight mocks to avoid ESM/SVG issues from CUIX/antd
jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: () => <input aria-label="filter" />
}));

jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

jest.mock('../sharedComponents/PageHeader', () => ({
  __esModule: true,
  default: () => <div data-testid="page-header">Header</div>
}));

// Mock InlineDescriptionEditor to avoid CUIX dependencies
jest.mock('../sharedComponents/InlineDescriptionEditor', () => ({
  __esModule: true,
  default: () => <span data-testid="inline-desc">Desc</span>
}));

// Mock CUIX Button LinkButton
jest.mock('cuix/dist/components/Button', () => ({
  __esModule: true,
  LinkButton: ({ children, onClick, ...rest }: any) => (
    <button onClick={onClick} {...rest}>
      {children}
    </button>
  )
}));

// Mock Toolbar to expose actions as buttons
jest.mock('../sharedComponents/Toolbar', () => ({
  __esModule: true,
  default: ({
    actions
  }: {
    actions: Array<{ key: string; label: string; onClick: () => void }>;
  }) => (
    <div>
      {actions.map(a => (
        <button key={a.key} onClick={a.onClick}>
          {a.label}
        </button>
      ))}
    </div>
  )
}));

// Mock Modal to always render and provide OK/Cancel buttons
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

// Mock PaginatedTable to render rows and expose selection
jest.mock('../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({
    data,
    onRowSelect
  }: {
    data: Array<{ name: string }>;
    onRowSelect?: (rows: any[]) => void;
  }) => (
    <div>
      <div data-testid="rows">
        {data.map((r, i) => (
          <div key={i}>{r.name}</div>
        ))}
      </div>
      {onRowSelect && <button onClick={() => onRowSelect(data as any[])}>Select All</button>}
    </div>
  )
}));

jest.mock('antd', () => {
  const Input = ({ value, onChange, placeholder }: any) => (
    <input value={value} onChange={onChange} placeholder={placeholder} />
  );
  // Attach TextArea as used in code
  // @ts-ignore
  Input.TextArea = ({ value, onChange, placeholder, rows }: any) => (
    <textarea value={value} onChange={onChange} placeholder={placeholder} data-rows={rows} />
  );

  return {
    __esModule: true,
    Input,
    Checkbox: ({ checked, onChange, children }: any) => (
      <label>
        <input type="checkbox" checked={checked} onChange={onChange} />
        {children}
      </label>
    )
  };
});

jest.mock('../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

describe('DatabasesList', () => {
  it('triggers drop of selected databases via confirmation modal', async () => {
    const user = userEvent.setup();
    const onDropDatabases = jest.fn();
    render(
      <DatabasesList
        databases={['default', 'sales']}
        isInitializing={false}
        isRefreshing={false}
        dbFilter=""
        setDbFilter={() => {}}
        dbPageNumber={1}
        setDbPageNumber={() => {}}
        dbPageSize={50}
        setDbPageSize={() => {}}
        dbDescriptions={{}}
        editingDb={null}
        editingValue=""
        setEditingDb={() => {}}
        setEditingValue={() => {}}
        onOpenDatabase={() => {}}
        onSaveDescription={() => {}}
        onDropDatabases={onDropDatabases}
      />
    );

    // Select all rows via mocked table
    await user.click(screen.getByText('Select All'));
    // Click Drop action button
    await user.click(screen.getByRole('button', { name: 'Drop' }));
    // Confirm OK in the visible modal
    const dropModal = screen.getAllByTestId('modal').find(m => !m.hasAttribute('hidden'))!;
    await user.click(within(dropModal).getByText('OK'));

    expect(onDropDatabases).toHaveBeenCalledWith(['default', 'sales']);
  });

  it('creates a new database via modal form', async () => {
    const user = userEvent.setup();
    const onCreateDatabase = jest.fn();

    render(
      <DatabasesList
        databases={[]}
        isInitializing={false}
        isRefreshing={false}
        dbFilter=""
        setDbFilter={() => {}}
        dbPageNumber={1}
        setDbPageNumber={() => {}}
        dbPageSize={50}
        setDbPageSize={() => {}}
        dbDescriptions={{}}
        editingDb={null}
        editingValue=""
        setEditingDb={() => {}}
        setEditingValue={() => {}}
        onOpenDatabase={() => {}}
        onSaveDescription={() => {}}
        onCreateDatabase={onCreateDatabase}
      />
    );

    // Open create modal via toolbar action
    await user.click(screen.getByRole('button', { name: 'New' }));

    // Fill name input
    const nameInput = screen.getByPlaceholderText('Database name');
    await user.type(nameInput, 'analytics');

    // Submit OK in the visible modal
    const createModal = screen.getAllByTestId('modal').find(m => !m.hasAttribute('hidden'))!;
    await user.click(within(createModal).getByText('OK'));

    expect(onCreateDatabase).toHaveBeenCalledWith('analytics', undefined, undefined);
  });
});
