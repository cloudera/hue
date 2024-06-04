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
import { render, waitFor, screen, within, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MetricsComponent from './MetricsComponent';
import userEvent from '@testing-library/user-event';

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
  }))
});

jest.mock('api/utils', () => ({
  get: jest.fn(() =>
    Promise.resolve({
      metric: {
        'queries.number': { value: 10 },
        'requests.active': { count: 5 },
        'requests.exceptions': { count: 2 },
        'requests.response-time': {
          '15m_rate': 20,
          '1m_rate': 15,
          '5m_rate': 18,
          '75_percentile': 50,
          '95_percentile': 60,
          '999_percentile': 70,
          '99_percentile': 55,
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

//1. Test for filtering metrics based on input
  
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

//2. Test for selecting a specific metric from the dropdown:

  test('selecting a specific metric from the dropdown filters the data', async () => {
    const { queryAllByRole, getByRole, getByText, queryByText } = render(
      <MetricsComponent />
    );

    // Wait for data to load
    await waitFor(() => getByText('queries.number'));

    // Verify that all data is loaded and displayed correctly
    let headings = queryAllByRole('heading', { level: 4 });
    console.log('Initial headings length:', headings.length);
    expect(headings).toHaveLength(9); // Check that there are 9 headings initially

    // Open the dropdown
    const dropdown = getByRole('combobox');
    console.log('Opening dropdown...');
    await userEvent.click(dropdown); // Simulate click to open dropdown
    
    // Wait for the dropdown options to be rendered
    const dropdownOptions = await waitFor(() => getByRole('listbox'));

    // Log text content of each option for debugging
    const options = within(dropdownOptions).getAllByRole('option');
    options.forEach(option => {
      console.log('Option:', option.textContent);
    });

    // Find and select the 'users' option
    const usersOption = options.find(option => option.textContent && option.textContent.toLowerCase().includes('users'));
    console.log('Users option found:', usersOption ? usersOption.textContent : 'None');
    expect(usersOption).toBeDefined();

    // Ensure the option is not undefined before clicking
    if (usersOption) {
      await userEvent.click(usersOption); // Select the 'users' option
    }

    // Wait for the UI to update and check the filtered data
    await waitFor(() => {
      headings = queryAllByRole('heading', { level: 4 });
      console.log('Headings length after filter:', headings.length);
      return headings.length === 1;
    });

    // Final assertions to ensure correct filtering
    headings = queryAllByRole('heading', { level: 4 });
    console.log('Final headings length:', headings.length);
    expect(headings).toHaveLength(1); // Only one heading should be present after filtering
    expect(headings[0]).toHaveTextContent('users'); // The visible heading should be 'users'

    // Ensure that 'queries.number' is no longer present after filtering
    expect(queryByText('queries.number')).toBeNull();
  });
});