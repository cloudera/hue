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
import '@testing-library/jest-dom';
import { render, screen, within, fireEvent } from '@testing-library/react';

import TableBrowserPage from './TableBrowserPage';

jest.mock('../../utils/huePubSub', () => ({
  __esModule: true,
  default: {
    publish: jest.fn(),
    subscribe: jest.fn(),
    remove: jest.fn()
  }
}));

// Lightweight mocks for external components
jest.mock('@cloudera/cuix-core/icons/react/DataBrowserIcon', () => ({
  __esModule: true,
  default: () => <span data-testid="icon" />
}));

jest.mock('../../reactComponents/CommonHeader/CommonHeader', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <div data-testid="header">{title}</div>
}));

jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title }: { title: string }) => <div>{title}</div>
}));

jest.mock('cuix/dist/components/Filter', () => ({
  __esModule: true,
  default: ({ onChange }: { onChange: (output: unknown) => void }) => (
    <input aria-label="filter" onChange={e => onChange({ search: [e.currentTarget.value] })} />
  )
}));

// Mock PaginatedTable to render the name column cell content so we can click the buttons
jest.mock('../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({ data, columns }: { data: any[]; columns: any[] }) => {
    const nameCol = columns.find((c: any) => c.dataIndex === 'name');
    return (
      <div data-testid="rows">
        {data.map((row, idx) => (
          <div key={idx} data-testid="row">
            {nameCol && nameCol.render ? nameCol.render(row.name, row) : row.name}
          </div>
        ))}
      </div>
    );
  }
}));

// Mock dataCatalog entry calls used by effects
jest.mock('../../catalog/dataCatalog', () => ({
  __esModule: true,
  default: {
    getEntry: jest.fn().mockResolvedValue({
      getChildren: jest.fn().mockResolvedValue([]),
      loadNavigatorMetaForChildren: jest.fn().mockResolvedValue([]),
      clearCache: jest.fn().mockResolvedValue(undefined),
      getAnalysis: jest.fn().mockResolvedValue({ properties: [], cols: [] }),
      getSample: jest.fn().mockResolvedValue({ meta: [], data: [] })
    })
  }
}));

// Mock useDataCatalog with simple in-memory state for connectors/databases/tables
jest.mock('../../utils/hooks/useDataCatalog/useDataCatalog', () => {
  const React = require('react');
  return {
    __esModule: true,
    useDataCatalog: () => {
      const connectors = React.useMemo(
        () => [
          { type: 'impala', id: 'impala' },
          { type: 'hive', id: 'hive' }
        ],
        []
      );
      const initialSource = (() => {
        const parts = (globalThis as any).location.pathname.split('/').filter(Boolean);
        const idx = parts.indexOf('tablebrowser');
        return idx !== -1 ? parts[idx + 1] : undefined;
      })();
      const initialConnector = connectors.find(c => c.type === initialSource) || null;
      const [connector, setConnector] = React.useState<any>(initialConnector);
      const [database, setDatabase] = React.useState<string | undefined>(undefined);
      const [tables, setTables] = React.useState<any[]>([]);

      const databases = connector ? ['default', 'sales'] : [];
      React.useEffect(() => {
        if (database) {
          setTables([
            { name: 'customers', type: 'table', comment: '' },
            { name: 'orders', type: 'table', comment: '' }
          ]);
        } else {
          setTables([]);
        }
      }, [database]);

      const stableNs = React.useMemo(() => ({ id: 'ns1' }), []);
      const stableCompute = React.useMemo(() => ({ id: 'c1' }), []);

      return {
        loading: {
          connector: false,
          namespace: false,
          compute: false,
          database: false,
          table: false
        },
        connectors,
        connector,
        namespace: stableNs,
        compute: stableCompute,
        databases,
        database,
        tables,
        setConnector,
        setDatabase,
        setNamespace: () => {},
        setCompute: () => {},
        reloadDatabases: async () => {},
        reloadTables: async () => {}
      } as any;
    }
  };
});

describe('TableBrowserPage breadcrumb navigation', () => {
  beforeEach(() => {
    // Start at /tablebrowser/impala to show databases
    window.history.pushState(null, '', '/tablebrowser/impala');
  });

  it('shows Databases for a selected source and navigates to Data sources', () => {
    const { unmount } = render(<TableBrowserPage />);
    expect(screen.getByText('Databases')).toBeInTheDocument();

    // Click Data sources crumb
    const dataSourcesLink = screen.getByText('Data sources');
    fireEvent.click(dataSourcesLink);

    // Should show sources list (buttons to open source exist)
    expect(screen.getAllByRole('button', { name: /open source/i }).length).toBeGreaterThan(0);
    unmount();
  });

  it('navigates from Data sources to a source, then to a database, then to a table, and back via crumbs', () => {
    // Go to sources page first
    window.history.pushState(null, '', '/tablebrowser/');
    const { unmount } = render(<TableBrowserPage />);

    // Click first source
    const rows = screen.getByTestId('rows');
    const sourceBtn = within(rows).getAllByRole('button', { name: /open source/i })[0];
    fireEvent.click(sourceBtn);

    // Should show databases
    expect(screen.getByText('Databases')).toBeInTheDocument();

    // Click first database (default)
    const dbRows = screen.getByTestId('rows');
    const dbButton = within(dbRows).getAllByRole('button', { name: /open database/i })[0];
    fireEvent.click(dbButton);

    // Should show tables
    expect(screen.getByText('Tables')).toBeInTheDocument();

    // Click first table (customers)
    const tblRows = screen.getByTestId('rows');
    const tableButton = within(tblRows).getAllByRole('button', { name: /open table/i })[0];
    fireEvent.click(tableButton);

    // Breadcrumb should show database crumb clickable, table as current
    expect(screen.getByText('customers')).toBeInTheDocument();

    // Click database crumb to go back to tables list
    const dbCrumb = screen.getByText('default');
    fireEvent.click(dbCrumb);
    expect(screen.getByText('Tables')).toBeInTheDocument();

    // Click Data sources crumb to go back to sources list
    const dataSourcesLink = screen.getByText('Data sources');
    fireEvent.click(dataSourcesLink);
    expect(screen.getAllByRole('button', { name: /open source/i }).length).toBeGreaterThan(0);
    unmount();
  });
});
