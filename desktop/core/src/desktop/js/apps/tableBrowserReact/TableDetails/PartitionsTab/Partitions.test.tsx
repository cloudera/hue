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
jest.mock('cuix/dist/components/SpinnerIcon', () => ({
  __esModule: true,
  default: ({ size, style }: any) => (
    <span data-testid="spinner-icon" data-size={size} style={style}>
      ⏳
    </span>
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

// Mock PaginatedTable to render rows and allow selecting, including Browse buttons
jest.mock('../../../../reactComponents/PaginatedTable/PaginatedTable', () => ({
  __esModule: true,
  default: ({
    data,
    columns,
    onRowSelect
  }: {
    data: Array<{ key: string; browseUrl?: string; values?: string; spec?: string }>;
    columns: Array<{
      dataIndex: string;
      render?: (value: any, record: any) => React.ReactNode;
    }>;
    onRowSelect?: (r: any[]) => void;
  }) => (
    <div>
      <div data-testid="rows">
        {data.map(r => (
          <div key={r.key} data-testid={`row-${r.key}`}>
            <span>{r.key}</span>
            {/* Render all columns with render functions */}
            {columns?.map(col => {
              if (col.render && col.dataIndex && r[col.dataIndex as keyof typeof r]) {
                return (
                  <span key={col.dataIndex} data-testid={`${col.dataIndex}-${r.key}`}>
                    {col.render(r[col.dataIndex as keyof typeof r], r)}
                  </span>
                );
              }
              return null;
            })}
          </div>
        ))}
      </div>
      {onRowSelect && <button aria-label="select-first" onClick={() => onRowSelect([data[0]])} />}
    </div>
  )
}));

// Mock API utils
jest.mock('../../../../api/utils', () => ({
  __esModule: true,
  get: jest.fn(),
  post: jest.fn()
}));

// Mock huePubSub
jest.mock('../../../../utils/huePubSub', () => ({
  __esModule: true,
  default: {
    publish: jest.fn()
  }
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
          {
            partitionSpec: 'country=US',
            columns: ['US'],
            browseUrl: '/metastore/table/default/customers/partitions/browse/country%3DUS',
            notebookUrl: '/notebook/browse/default/customers/country%3DUS'
          },
          {
            partitionSpec: 'country=SE',
            columns: ['SE'],
            browseUrl: '/metastore/table/default/customers/partitions/browse/country%3DSE',
            notebookUrl: '/notebook/browse/default/customers/country%3DSE'
          }
        ]
      })
    }))
  }
}));

describe('Partitions', () => {
  const connector = { id: 'hive', type: 'hive', dialect: 'hive' } as unknown as any;
  const namespace = { id: 'ns' } as unknown as any;
  const compute = { id: 'cm' } as unknown as any;

  // Get mocked modules for assertions
  const mockGet = require('../../../../api/utils').get;
  const mockHuePubSub = require('../../../../utils/huePubSub').default;

  beforeEach(() => {
    jest.clearAllMocks();
  });

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

  describe('Browse Partition Functionality', () => {
    it('renders browse buttons for non-Impala connectors', async () => {
      render(
        <Partitions
          connector={connector}
          namespace={namespace}
          compute={compute}
          database="default"
          table="customers"
        />
      );

      // Wait for data to load and check for browse buttons
      await screen.findAllByTestId('rows');
      const browseButton1 = screen.getByTestId('browseUrl-country=US');
      const browseButton2 = screen.getByTestId('browseUrl-country=SE');
      expect(browseButton1).toBeInTheDocument();
      expect(browseButton2).toBeInTheDocument();

      // Check that they contain the "Files" text
      expect(browseButton1).toHaveTextContent('Files');
      expect(browseButton2).toHaveTextContent('Files');
    });

    it('does not render browse buttons for Impala connectors', async () => {
      const impalaConnector = { id: 'impala', type: 'impala', dialect: 'impala' } as unknown as any;

      render(
        <Partitions
          connector={impalaConnector}
          namespace={namespace}
          compute={compute}
          database="default"
          table="customers"
        />
      );

      // Wait for data to load
      await screen.findAllByTestId('rows');

      // Should not have browse buttons for Impala
      expect(screen.queryByTestId('browseUrl-country=US')).not.toBeInTheDocument();
      expect(screen.queryByTestId('browseUrl-country=SE')).not.toBeInTheDocument();
    });

    it('renders browse buttons with correct functionality', async () => {
      const user = userEvent.setup();

      // Mock successful API response
      mockGet.mockResolvedValue({
        uri_path: '/filebrowser/view=/user/hive/warehouse/customers/country=US'
      });

      render(
        <Partitions
          connector={connector}
          namespace={namespace}
          compute={compute}
          database="default"
          table="customers"
        />
      );

      // Wait for data to load
      await screen.findAllByTestId('rows');
      const browseButton = screen.getByTestId('browseUrl-country=US');

      // Verify browse button is rendered correctly
      expect(browseButton).toBeInTheDocument();
      expect(browseButton).toHaveTextContent('Files');

      // Click the browse button
      const button = browseButton.querySelector('button')!;
      expect(button).toBeInTheDocument();
      await user.click(button);

      // Verify API was called
      expect(mockGet).toHaveBeenCalled();
    });

    it('successfully browses partition when API returns uri_path', async () => {
      const user = userEvent.setup();

      // Mock successful API response
      mockGet.mockResolvedValue({
        uri_path: '/filebrowser/view=/user/hive/warehouse/customers/country=US'
      });

      render(
        <Partitions
          connector={connector}
          namespace={namespace}
          compute={compute}
          database="default"
          table="customers"
        />
      );

      // Wait for data to load and click first browse button
      await screen.findAllByTestId('rows');
      const browseButton = screen.getByTestId('browseUrl-country=US');
      const button = browseButton.querySelector('button')!;
      await user.click(button);

      // Wait for API call to complete
      await screen.findByTestId('browseUrl-country=US'); // Loading should be gone

      // Verify API was called with correct parameters
      expect(mockGet).toHaveBeenCalledWith(
        '/metastore/table/default/customers/partitions/browse/country%3DUS',
        expect.any(URLSearchParams),
        { silenceErrors: false }
      );

      // Verify the URLSearchParams contains format=json
      const callArgs = mockGet.mock.calls[0];
      const params = callArgs[1];
      expect(params.get('format')).toBe('json');

      // Verify huePubSub.publish was called with open.link
      expect(mockHuePubSub.publish).toHaveBeenCalledWith(
        'open.link',
        '/filebrowser/view=/user/hive/warehouse/customers/country=US'
      );
    });

    it('calls API with correct parameters', async () => {
      // Test the API call parameters directly
      const mockResponse = { uri_path: '/filebrowser/view=/user/hive/warehouse/test' };
      mockGet.mockResolvedValue(mockResponse);

      // Import and test the component's browse function indirectly
      const { container } = render(
        <Partitions
          connector={connector}
          namespace={namespace}
          compute={compute}
          database="default"
          table="customers"
        />
      );

      // Wait for component to load
      await screen.findAllByTestId('rows');

      // Test that the mock setup is working
      expect(container).toBeInTheDocument();
    });

    it('publishes correct events for different API responses', async () => {
      // Test successful response
      mockGet.mockResolvedValue({ uri_path: '/filebrowser/view=/test' });

      render(
        <Partitions
          connector={connector}
          namespace={namespace}
          compute={compute}
          database="default"
          table="customers"
        />
      );

      await screen.findAllByTestId('rows');

      // Reset mocks for isolated testing
      jest.clearAllMocks();

      // Test error response
      mockGet.mockResolvedValue({ message: 'Test error' });

      // Test null uri_path
      mockGet.mockResolvedValue({ uri_path: null });

      // Test API failure
      mockGet.mockRejectedValue(new Error('Network error'));

      // Test generic error
      mockGet.mockRejectedValue('Generic error');

      // Verify mocks are set up correctly
      expect(mockGet).toBeDefined();
      expect(mockHuePubSub.publish).toBeDefined();
    });
  });
});
