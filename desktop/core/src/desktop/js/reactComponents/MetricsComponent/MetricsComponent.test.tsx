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
import MetricsComponent from './MetricsComponent';

// Mock the API call to return sample metrics data
jest.mock('api/utils', () => ({
  get: jest.fn(() =>
    Promise.resolve({
      metric: {
        'queries.number': { value: 10 },
        'requests.active': { count: 5 },
        'requests.exceptions': { count: 2 },
        'requests.response-time': {
          '1m_rate': 15,
          '15m_rate': 20,
          '5m_rate': 18,
          '75_percentile': 50,
          '95_percentile': 60,
          '99_percentile': 55,
          '999_percentile': 70,
          avg: 25,
          count: 100,
          max: 30,
          mean_rate: 22,
          min: 20,
          std_dev: 5,
          sum: 2500
        },
        'threads.daemon': { value: 3 },
        'threads.total': { value: 6 },
        users: { value: 50 },
        'users.active': { value: 30 },
        'users.active.total': { value: 40 }
      }
    })
  )
}));

describe('MetricsComponent', () => {
  test('Filtering metrics based on name column value', async () => {
    render(<MetricsComponent />);

    const filterInput = screen.getByPlaceholderText('Filter metrics...');
    fireEvent.change(filterInput, { target: { value: 'value' } });

    await waitFor(() => {
      expect(screen.getByText('queries.number')).toBeInTheDocument();
      expect(screen.getByText('threads.daemon')).toBeInTheDocument();
      expect(screen.getByText('threads.total')).toBeInTheDocument();
      expect(screen.getByText('users')).toBeInTheDocument();
      expect(screen.getByText('users.active')).toBeInTheDocument();
      expect(screen.getByText('users.active.total')).toBeInTheDocument();
      expect(screen.queryByText('requests.active')).not.toBeInTheDocument();
      expect(screen.queryByText('requests.exceptions')).toBeNull();
      expect(screen.queryByText('requests.response-time')).toBeNull();
    });
  });

  test('selecting a specific metric from the dropdown filters the data using click events', async () => {
    render(<MetricsComponent />);

    await waitFor(() => screen.getByText('queries.number'));

    const select = screen.getByTestId('metric-select').firstElementChild;
    if (select) {
      fireEvent.mouseDown(select);
    }

    const dropdown = document.querySelector('.ant-select');

    const secondOption = dropdown?.querySelectorAll('.ant-select-item')[1];
    if (secondOption) {
      fireEvent.click(secondOption);
      await waitFor(() => {
        const headings = screen.queryAllByRole('heading', { level: 4 });
        expect(headings).toHaveLength(1);
      });
    }
  });

  test('ensuring metrics starting with auth, multiprocessing and python.gc are not displayed', async () => {
    jest.clearAllMocks();
    jest.mock('api/utils', () => ({
      get: jest.fn(() =>
        Promise.resolve({
          metric: {
            'auth.ldap.auth-time': {
              '1m_rate': 20,
              '5m_rate': 15,
              '15m_rate': 30,
              '75_percentile': 50,
              '95_percentile': 60,
              '99_percentile': 55,
              '999_percentile': 70,
              avg: 25,
              count: 100,
              max: 30,
              mean_rate: 22,
              min: 20,
              std_dev: 5,
              sum: 2000
            },
            'multiprocessing.processes.total': { value: 5 },
            'python.gc.objects': { value: 2 },
            users: { value: 50 }
          }
        })
      )
    }));
    render(<MetricsComponent />);

    await waitFor(() => {
      expect(screen.queryByText('auth.ldap.auth-time')).not.toBeInTheDocument();
      expect(screen.queryByText('multiprocessing.processes.total')).not.toBeInTheDocument();
      expect(screen.queryByText('python.gc.objects')).not.toBeInTheDocument();
      expect(screen.queryByText('users')).toBeInTheDocument();
    });
  });
});
