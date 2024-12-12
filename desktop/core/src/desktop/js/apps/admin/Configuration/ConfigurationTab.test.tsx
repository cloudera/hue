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
import '@testing-library/jest-dom';
import Configuration from './ConfigurationTab';
import { ConfigurationKey } from './ConfigurationKey';
import { ConfigurationValue } from './ConfigurationValue';
import ApiHelper from '../../../api/apiHelper';

// Mock API call to fetch configuration data
jest.mock('../../../api/apiHelper', () => ({
  fetchHueConfigAsync: jest.fn()
}));

beforeEach(() => {
  jest.clearAllMocks();
  ApiHelper.fetchHueConfigAsync = jest.fn(() =>
    Promise.resolve({
      apps: [{ name: 'desktop', has_ui: true, display_name: 'Desktop' }],
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
        }
      ],
      conf_dir: '/conf/directory'
    })
  );
});

describe('Configuration Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('Renders Configuration component with fetched data', async () => {
    render(<Configuration />);

    await waitFor(() => {
      expect(screen.getByText(/Sections/i)).toBeInTheDocument();
      expect(screen.getByText(/Desktop/i)).toBeInTheDocument();
      expect(screen.getByText(/example\.config/i)).toBeInTheDocument();
      expect(screen.getByText(/Example value/i)).toBeInTheDocument();
      expect(ApiHelper.fetchHueConfigAsync).toHaveBeenCalled();
    });
  });

  test('Filters configuration based on input text', async () => {
    render(<Configuration />);

    const filterInput = screen.getByPlaceholderText('Filter in desktop...');
    fireEvent.change(filterInput, { target: { value: 'another' } });

    await waitFor(() => {
      expect(screen.queryByText('example.config')).not.toBeInTheDocument();
      expect(screen.getByText('another.config')).toBeInTheDocument();
    });
  });

  test('Displays message for empty configuration section', async () => {
    (ApiHelper.fetchHueConfigAsync as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        apps: [{ name: 'desktop', has_ui: true, display_name: 'Desktop' }],
        config: [{ help: 'No help available.', key: 'desktop', is_anonymous: false, values: [] }],
        conf_dir: '/conf/directory'
      })
    );

    render(<Configuration />);

    await waitFor(() => screen.getByText('Empty configuration section'));
    expect(screen.getByText('Empty configuration section')).toBeInTheDocument();
  });

  describe('ConfigurationKey Component', () => {
    test('If the record has further values in it, should display record key, helpText as tooltip', () => {
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
  });

  test('If the record has no further values in it, verifies the entire config key state', () => {
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

  test('renders "Default section" and help text as tooltip for anonymous records', () => {
    const record = { is_anonymous: true, help: 'Help info', key: 'config.key' };
    const { getByText, container } = render(<ConfigurationKey record={record} />);

    expect(getByText(/Default section/i)).toBeInTheDocument();

    const tooltip = container.querySelector('.config__help-tooltip');
    expect(tooltip).toBeInTheDocument();
  });

  describe('ConfigurationValue Component', () => {
    test('If the record has further values in it, renders nested configuration key and values correctly', () => {
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
  });

  test('If the record has no further values in it, renders nothing', () => {
    const mockRecord = { help: '', key: 'empty.config', is_anonymous: false };

    const { container } = render(<ConfigurationValue record={mockRecord} />);

    expect(container).toBeEmptyDOMElement();
  });
});
