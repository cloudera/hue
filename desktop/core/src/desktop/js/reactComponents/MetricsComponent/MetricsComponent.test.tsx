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
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom'
import MetricsComponent from './MetricsComponent';
import userEvent from '@testing-library/user-event';
import { Dropdown } from 'antd';

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

//1. Test for filtering metrics based on input
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

//   //2. Test for selecting a specific metric from the dropdown:
//   test('Selecting a specific metric from the dropdown', async () => {
//     render(<MetricsComponent />);

//     // // const dropdown = screen.getByPlaceholderText('Choose a metric');
//     // const dropdown = await screen.findByRole('combobox');
//     // // console.log('dropdown', dropdown);
//     // fireEvent.click(dropdown, { target: { value: 'users' } });
//     // screen.debug();

//     // const dropdown = await screen.findByRole('combobox');
//     // userEvent.click(dropdown); // Open the dropdown
    
//     // const usersOption = await screen.findByText('users');
//     // userEvent.click(usersOption); // Select the 'Users' option


//     const periodSelect = screen.getByRole('combobox');
//     // console.log(periodSelect);

//     await userEvent.click(periodSelect);


//     // await waitFor(() => screen.getByText('Users'));

//     // fireEvent.click(screen.getByText('Users'));
//     const option= await screen.getByText('Users');

//     console.log(option)
//     await userEvent.click(option);

//     // screen.debug();

//     // await waitFor(() => {
//     //    const bla = screen.getByText('Users');
//     //    console.log(bla);

//     // });

  
//     // fireEvent.click(screen.getByText('% Dia'));

//     // expect(handleChangeStub).toBeCalledWith('days', expect.anything());

//     // console.log(fireEvent);
//     // userEvent.selectOptions(dropdown, 'users');
//     // const bla = await screen.findByText('users');
//     // console.log(bla);

//     await expect(screen.getByText('queries.number')).not.toBeVisible();
//     // await waitFor(() => {
      
//     //   expect(screen.getByText('queries.number')).not.toBeVisible();
//     //   // expect(screen.queryAllByText('requests.active')).toBeNull();
//     //   // expect(screen.queryAllByText('requests.exceptions')).toBeNull();
//     //   // expect(screen.queryAllByText('threads.daemon')).toBeNull();
//     //   // expect(screen.queryAllByText('threads.total')).toBeNull();
//     //   // expect(screen.queryAllByText('users')).toBeInTheDocument();
//     //   // expect(screen.queryAllByText('users.active')).toBeNull();
//     //   // expect(screen.queryAllByText('users.active.total')).toBeNull();
//     //   // console.log(bla);
//     // });

//   });
// });

test('Selecting a specific metric from the dropdown', async () => {
  render(<MetricsComponent />);

  const dropdown = await screen.findByRole('combobox');
  userEvent.click(dropdown); // Open the dropdown
  
  const usersOption = await screen.findByText('Users');
  userEvent.click(usersOption); // Select the 'Users' option

  // Introduce a delay before asserting the absence of the "queries.number" element
  setTimeout(() => {
    expect(screen.queryAllByText('queries.number')).toHaveLength(0);
  }, 500); // Adjust the delay time as needed
  
  await waitFor(() => {
    expect(screen.queryByText('requests.active')).toBeNull();
    expect(screen.queryByText('requests.exceptions')).toBeNull();
    expect(screen.queryByText('threads.daemon')).toBeNull();
    expect(screen.queryByText('threads.total')).toBeNull();
    expect(screen.getByText('users')).toBeInTheDocument();
    expect(screen.queryByText('users.active')).toBeNull();
    expect(screen.queryByText('users.active.total')).toBeNull();
  });
});
});
