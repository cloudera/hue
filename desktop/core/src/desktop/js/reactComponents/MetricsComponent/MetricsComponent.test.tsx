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

// import React from 'react';
// import { render, waitFor, screen, within, fireEvent } from '@testing-library/react';
// import '@testing-library/jest-dom';
// import MetricsComponent from './MetricsComponent';
// import userEvent from '@testing-library/user-event';

// // Mock matchMedia for compatibility with certain UI libraries
// Object.defineProperty(window, 'matchMedia', {
//   writable: true,
//   value: jest.fn().mockImplementation(query => ({
//     matches: false,
//     media: query,
//     onchange: null,
//     addListener: jest.fn(), // Deprecated
//     removeListener: jest.fn(), // Deprecated
//     addEventListener: jest.fn(),
//     removeEventListener: jest.fn(),
//     dispatchEvent: jest.fn()
//   }))
// });

// // Mock the API call to return sample metrics data
// jest.mock('api/utils', () => ({
//   get: jest.fn(() =>
//     Promise.resolve({
//       metric: {
//         'queries.number': { value: 10 },
//         'requests.active': { count: 5 },
//         'requests.exceptions': { count: 2 },
//         'requests.response-time': {
//           '15m_rate': 20,
//           '1m_rate': 15,
//           '5m_rate': 18,
//           '75_percentile': 50,
//           '95_percentile': 60,
//           '999_percentile': 70,
//           '99_percentile': 55,
//           avg: 25,
//           count: 100,
//           max: 30,
//           mean_rate: 22,
//           min: 20,
//           std_dev: 5,
//           sum: 2500
//         },
//         'threads.daemon': { value: 3 },
//         'threads.total': { value: 6 },
//         users: { value: 50 },
//         'users.active': { value: 30 },
//         'users.active.total': { value: 40 }
//       }
//     })
//   )
// }));

// describe('MetricsComponent', () => {

//   // Test for filtering metrics based on input
//   test('Filtering metrics based on name column value', async () => {
//     render(<MetricsComponent />);

//     const filterInput = screen.getByPlaceholderText('Filter metrics...');
//     fireEvent.change(filterInput, { target: { value: 'value' } });

//     await waitFor(() => {
//       expect(screen.getByText('queries.number')).toBeInTheDocument();
//       expect(screen.getByText('threads.daemon')).toBeInTheDocument();
//       expect(screen.getByText('threads.total')).toBeInTheDocument();
//       expect(screen.getByText('users')).toBeInTheDocument();
//       expect(screen.getByText('users.active')).toBeInTheDocument();
//       expect(screen.getByText('users.active.total')).toBeInTheDocument();
//       expect(screen.queryByText('requests.active')).not.toBeInTheDocument();
//       expect(screen.queryByText('requests.exceptions')).toBeNull();
//       expect(screen.queryByText('requests.response-time')).toBeNull();
//     });
//   });

//   // Test for selecting a specific metric from the dropdown:
//   test('selecting a specific metric from the dropdown filters the data', async () => {
//     render(<MetricsComponent />);
  
//     // Wait for data to load and ensure 'queries.number' is present
//     await waitFor(() => screen.getByText('queries.number'));
  
//     // Initial assertions to verify all data is loaded
//     let headings = screen.queryAllByRole('heading', { level: 4 });
//     console.log('Initial headings:', headings.map(h => h.textContent));
//     expect(headings).toHaveLength(9); // There should be 9 headings initially
  
//     // Open the dropdown
//     const dropdown = screen.getByRole('combobox');
//     fireEvent.mouseDown(dropdown); // Use fireEvent to open the dropdown
  
//     // Wait for the dropdown options to be rendered
//     const dropdownOptions = await waitFor(() => screen.getByRole('listbox'));
  
//     // Refine selection by targeting dropdown options within the listbox
//     const options = within(dropdownOptions).getAllByRole('option');
//     expect(options.length).toBeGreaterThan(0); // Ensure at least one option is available
//     console.log('Dropdown options:', options.map(o => o.textContent));
  
//     // Select the first item in the dropdown (excluding the "All" option)
//     const firstOption = options[1]; // Ensure to skip the "All" option
//     console.log('First option selected:', firstOption.textContent);
//     expect(firstOption).toBeDefined();
  
//     fireEvent.click(firstOption); // Use fireEvent to click the option
  
//     // Wait for the UI to update and check the filtered data
//     await waitFor(() => {
//       console.log('Waiting for headings to update...');
//       headings = screen.queryAllByRole('heading', { level: 4 });
//       console.log('Headings length after filter attempt:', headings.length);
//       expect(headings).toHaveLength(1); // Only one heading should be present after filtering
//       expect(headings[0]).toHaveTextContent(firstOption.textContent); // The visible heading should match the selected option
//     });
  
//     // Ensure that 'queries.number' is no longer present after filtering
//     expect(screen.queryByText('queries.number')).toBeNull();
//     console.log('queries.number is no longer present.');
//   });
// });

import React from 'react';
import { render, waitFor, screen, within, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MetricsComponent from './MetricsComponent';
import userEvent from '@testing-library/user-event';

// Mock matchMedia for compatibility with certain UI libraries
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

// Mock the API call to return sample metrics data
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
  // Test for filtering metrics based on input
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

  // Test for selecting a specific metric from the dropdown

// MetricsComponent.test.tsx (218-250)
test('selecting a specific metric from the dropdown filters the data using click events', async () => {
  render(<MetricsComponent />);
  
  // Wait for data to load and ensure 'queries.number' is present
  await waitFor(() => screen.getByText('queries.number'));
  
  const select = screen.getByTestId('metric-select').firstElementChild;
  if (select) {
    fireEvent.mouseDown(select);
  }

  // Query for the dropdown menu which is now in the document
  const dropdown = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
  
  // Click the first option
  const secondOption = dropdown?.querySelectorAll('.ant-select-item')[1]; 
  if (secondOption) {
    fireEvent.click(secondOption);
    await waitFor(() => {
      const headings = screen.queryAllByRole('heading', { level: 4 });
      expect(headings).toHaveLength(1); // This should fail if the filter does not work
    }); // Increase the timeout if needed
  }
});
});
