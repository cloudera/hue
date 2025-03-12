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
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ServerLogs from './ServerLogsTab';
import { mocked } from 'jest-mock';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

const mockData = jest.fn().mockReturnValue({
  logs: ['Log entry 1', 'Log entry 2'],
  hueHostname: 'test-hostname'
});

const emptyMockData = jest.fn().mockReturnValue({
  logs: [],
  hueHostname: 'test-hostname'
});

jest.mock('../../../utils/hooks/useLoadData/useLoadData');

afterEach(() => {
  jest.clearAllMocks();
});

describe('ServerLogs Component', () => {
  it('should render ServerLogs component with fetched logs', () => {
    mocked(useLoadData).mockImplementation(() => ({
      data: mockData(),
      loading: false,
      reloadData: jest.fn()
    }));

    render(<ServerLogs />);

    expect(screen.getByText('Log entry 1')).toBeInTheDocument();
    expect(screen.getByText('Log entry 2')).toBeInTheDocument();
  });

  test('it should handle the scenario when no logs are found', () => {
    mocked(useLoadData).mockImplementation(() => ({
      data: emptyMockData(),
      loading: false,
      reloadData: jest.fn()
    }));

    render(<ServerLogs />);

    expect(screen.getByText('No logs found!')).toBeInTheDocument();
  });

  test('it should find and highlights the searched value', async () => {
    mocked(useLoadData).mockImplementation(() => ({
      data: mockData(),
      loading: false,
      reloadData: jest.fn()
    }));

    render(<ServerLogs />);

    const searchValue = 'entry 1';
    const searchInput = screen.getByPlaceholderText('Search in the logs');

    await userEvent.type(searchInput, searchValue);

    const highlightedElements = screen.getAllByText(searchValue, { selector: 'mark' });
    expect(highlightedElements.length).toBeGreaterThan(0);
    highlightedElements.forEach(element => {
      expect(element).toHaveClass('server--highlight-word');
    });
  });

  test('it should wrap the logs when the user checks "Wrap logs"', async () => {
    mocked(useLoadData).mockImplementation(() => ({
      data: mockData(),
      loading: false,
      reloadData: jest.fn()
    }));

    render(<ServerLogs />);

    expect(screen.getByLabelText('Wrap logs')).toBeChecked();
    expect(screen.getByText('Log entry 1')).toHaveClass('server__log-line--wrap');

    fireEvent.click(screen.getByLabelText('Wrap logs'));
    expect(screen.getByLabelText('Wrap logs')).not.toBeChecked();
    expect(screen.getByText('Log entry 1')).not.toHaveClass('server__log-line--wrap');
  });
});
