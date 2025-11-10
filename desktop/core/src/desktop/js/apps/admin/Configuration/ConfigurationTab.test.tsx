// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { render, waitFor, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import Configuration from './ConfigurationTab';
import { ConfigurationKey } from './ConfigurationKey';
import { ConfigurationValue } from './ConfigurationValue';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

jest.mock('../../../utils/hooks/useLoadData/useLoadData');

const mockUseLoadData = useLoadData as jest.MockedFunction<typeof useLoadData>;

const mockData = {
  apps: [
    { name: 'desktop', has_ui: true, display_name: 'Desktop' },
    { name: 'test', has_ui: true, display_name: 'test' }
  ],
  config: [
    {
      help: 'Main configuration section',
      key: 'desktop',
      is_anonymous: false,
      values: [
        {
          help: 'Example config help text',
          key: 'example.config',
          is_anonymous: false,
          value: 'Example value'
        },
        {
          help: 'Another config help text',
          key: 'another.config',
          is_anonymous: false,
          value: 'Another value'
        }
      ]
    },
    {
      help: '',
      key: 'test',
      is_anonymous: false,
      values: [
        {
          help: 'Example config help text2',
          key: 'test.config2',
          is_anonymous: false,
          value: 'Hello World'
        }
      ]
    }
  ],
  conf_dir: '/conf/directory'
};

beforeEach(() => {
  jest.clearAllMocks();
  mockUseLoadData.mockReturnValue({
    data: mockData,
    loading: false,
    error: undefined,
    reloadData: jest.fn()
  });
});

describe('Configuration Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading and Error States', () => {
    test('Displays loading spinner when data is being fetched', () => {
      mockUseLoadData.mockReturnValue({
        data: undefined,
        loading: true,
        error: undefined,
        reloadData: jest.fn()
      });

      render(<Configuration />);

      const spinners = screen.getAllByTestId('loading-error-wrapper__spinner');
      expect(spinners.length).toBeGreaterThan(0);
      expect(spinners[0]).toBeInTheDocument();
    });

    test('Displays error message when API call fails', async () => {
      mockUseLoadData.mockReturnValue({
        data: undefined,
        loading: false,
        error: 'Failed to fetch configuration',
        reloadData: jest.fn()
      });

      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByText('Failed loading configuration')).toBeInTheDocument();
        expect(screen.getByText('Failed to fetch configuration')).toBeInTheDocument();
      });
    });

    test('Retry button refetches data after error', async () => {
      const mockReloadData = jest.fn();
      mockUseLoadData.mockReturnValue({
        data: undefined,
        loading: false,
        error: 'Failed to fetch configuration',
        reloadData: mockReloadData
      });

      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByText('Failed loading configuration')).toBeInTheDocument();
      });

      const user = userEvent.setup();
      const retryButton = screen.getByRole('button', { name: /Retry/i });
      await user.click(retryButton);

      await waitFor(() => {
        expect(mockReloadData).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Rendering Configuration Data', () => {
    test('Renders Configuration component with fetched data for default desktop section', async () => {
      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByText(/Sections/i)).toBeInTheDocument();
        expect(screen.getByText(/Desktop/i)).toBeInTheDocument();
        expect(screen.getByText(/example\.config/i)).toBeInTheDocument();
        expect(screen.getByText(/Example value/i)).toBeInTheDocument();
      });
    });

    test('Displays configuration directory path', async () => {
      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByText('/conf/directory')).toBeInTheDocument();
      });
    });

    test('Displays message for empty configuration section', async () => {
      mockUseLoadData.mockReturnValue({
        data: {
          apps: [{ name: 'desktop', has_ui: true, display_name: 'Desktop' }],
          config: [{ help: 'No help available.', key: 'desktop', is_anonymous: false, values: [] }],
          conf_dir: '/conf/directory'
        },
        loading: false,
        error: undefined,
        reloadData: jest.fn()
      });

      render(<Configuration />);

      await waitFor(() => screen.getByText('Empty configuration section'));
      expect(screen.getByText('Empty configuration section')).toBeInTheDocument();
    });
  });

  describe('Section Selection', () => {
    test('Shows all sections when ALL option is selected', async () => {
      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByText(/Sections/i)).toBeInTheDocument();
        expect(screen.getByText(/Desktop/i)).toBeInTheDocument();
        expect(screen.getByText(/example\.config/i)).toBeInTheDocument();
        expect(screen.getByText(/Example value/i)).toBeInTheDocument();
        expect(screen.queryAllByText(/test/i)).toHaveLength(0);
      });

      const user = userEvent.setup();

      const select = screen.getByRole('combobox');
      await user.click(select);

      const allOption = await screen.findByTitle('ALL');
      await user.click(allOption);

      await waitFor(() => {
        expect(screen.getAllByText(/test/i)).toHaveLength(3);
        expect(screen.getByText(/test\.config2/i)).toBeInTheDocument();
        expect(screen.getByText(/Hello World/i)).toBeInTheDocument();
      });
    });

    test('Switches to specific section when selected from dropdown', async () => {
      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByText(/example\.config/i)).toBeInTheDocument();
        expect(screen.queryByText(/test\.config2/i)).not.toBeInTheDocument();
      });

      const user = userEvent.setup();
      const select = screen.getByRole('combobox');
      await user.click(select);

      const testOption = await screen.findByTitle('test');
      await user.click(testOption);

      await waitFor(() => {
        expect(screen.queryByText(/example\.config/i)).not.toBeInTheDocument();
        expect(screen.getByText(/test\.config2/i)).toBeInTheDocument();
        expect(screen.getByText(/Hello World/i)).toBeInTheDocument();
      });
    });
  });

  describe('Filtering Configuration', () => {
    test('Filters configuration based on key name', async () => {
      render(<Configuration />);

      const filterInput = screen.getByPlaceholderText('Filter in desktop...');
      fireEvent.change(filterInput, { target: { value: 'another' } });

      await waitFor(() => {
        expect(screen.queryByText('example.config')).not.toBeInTheDocument();
        expect(screen.getByText('another.config')).toBeInTheDocument();
      });
    });

    test('Filters configuration based on help text', async () => {
      render(<Configuration />);

      const filterInput = screen.getByPlaceholderText('Filter in desktop...');
      fireEvent.change(filterInput, { target: { value: 'Example config help' } });

      await waitFor(() => {
        expect(screen.getByText('example.config')).toBeInTheDocument();
        expect(screen.queryByText('another.config')).not.toBeInTheDocument();
      });
    });

    test('Shows placeholder text based on selected section', async () => {
      render(<Configuration />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Filter in desktop...')).toBeInTheDocument();
      });

      const user = userEvent.setup();
      const select = screen.getByRole('combobox');
      await user.click(select);

      const allOption = await screen.findByTitle('ALL');
      await user.click(allOption);

      await waitFor(() => {
        expect(screen.getByPlaceholderText('Filter...')).toBeInTheDocument();
      });
    });
  });

  describe('ConfigurationKey Component', () => {
    test('Displays record key and help text as tooltip for parent records with nested values', () => {
      const mockRecord = {
        help: 'This is help text',
        key: 'config.key',
        is_anonymous: false,
        values: [
          {
            help: 'Example config help text',
            key: 'example.config',
            is_anonymous: false,
            value: 'Example value'
          },
          {
            help: 'Another config help text',
            key: 'another.config',
            is_anonymous: false,
            value: 'Another value'
          }
        ]
      };

      const { getByText, container } = render(<ConfigurationKey record={mockRecord} />);

      expect(getByText(/config.key/i)).toBeInTheDocument();
      const tooltip = container.querySelector('.config__help-tooltip');
      expect(tooltip).toBeInTheDocument();
    });

    test('Displays complete config details for leaf records without nested values', () => {
      const record = {
        is_anonymous: false,
        key: 'Last Config Key',
        value: 'Some Value',
        help: 'Help info',
        default: 'Default Value'
      };
      const { getByText, container } = render(<ConfigurationKey record={record} />);

      expect(getByText('Last Config Key')).toBeInTheDocument();
      expect(getByText('Some Value')).toBeInTheDocument();
      expect(getByText(/Help info/i)).toBeInTheDocument();
      expect(getByText(/Default: Default Value/i)).toBeInTheDocument();

      const tooltip = container.querySelector('.config__help-tooltip');
      expect(tooltip).not.toBeInTheDocument();
    });

    test('Renders "Default section" with help tooltip for anonymous records', () => {
      const record = { is_anonymous: true, help: 'Help info', key: 'config.key' };
      const { getByText, container } = render(<ConfigurationKey record={record} />);

      expect(getByText(/Default section/i)).toBeInTheDocument();

      const tooltip = container.querySelector('.config__help-tooltip');
      expect(tooltip).toBeInTheDocument();
    });
  });

  describe('ConfigurationValue Component', () => {
    test('Renders nested configuration keys and values for parent records', () => {
      const mockRecord = {
        help: '',
        key: 'parent.config',
        is_anonymous: false,
        values: [
          {
            help: 'child config help',
            key: 'child.config',
            is_anonymous: false,
            value: 'child value'
          }
        ]
      };

      render(<ConfigurationValue record={mockRecord} />);

      expect(screen.getByText('child.config')).toBeInTheDocument();
      expect(screen.getByText('child value')).toBeInTheDocument();
      expect(screen.queryByText('parent.config')).not.toBeInTheDocument();
    });

    test('Renders nothing for leaf records without nested values', () => {
      const mockRecord = { help: '', key: 'empty.config', is_anonymous: false };

      const { container } = render(<ConfigurationValue record={mockRecord} />);

      expect(container).toBeEmptyDOMElement();
    });
  });
});
