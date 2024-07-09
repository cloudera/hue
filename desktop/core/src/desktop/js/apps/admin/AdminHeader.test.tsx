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
import { render, fireEvent, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminHeader from './AdminHeader';

// Mock data for the component
const options = ['Option 1', 'Option 2', 'Option 3'];
const mockOnSelectChange = jest.fn();
const mockOnFilterChange = jest.fn();

test('renders AdminHeader with correct dropdown and input filter', () => {
  render(
    <AdminHeader
      options={options}
      selectedValue="Option 1"
      onSelectChange={mockOnSelectChange}
      filterValue=""
      onFilterChange={mockOnFilterChange}
      placeholder="Filter data..."
    />
  );

  expect(screen.getByText('Option 1')).toBeInTheDocument();
  expect(screen.queryByText('Option 2')).not.toBeInTheDocument();
  expect(screen.queryByText('Option 3')).not.toBeInTheDocument();

  expect(screen.getByPlaceholderText('Filter data...')).toBeInTheDocument();
});

test('Calls onSelectChange with correct value when a different option is selected from the dropdown', async () => {
  render(
    <AdminHeader
      options={options}
      selectedValue="Option 1"
      onSelectChange={mockOnSelectChange}
      filterValue=""
      onFilterChange={mockOnFilterChange}
      placeholder="Filter data..."
    />
  );

  const selectDropdown = screen.getByTestId('admin-header--select').firstElementChild;

  if (selectDropdown) {
    fireEvent.mouseDown(selectDropdown);
  }

  const dropdown = document.querySelector('.ant-select');

  const secondOption = dropdown?.querySelectorAll('.ant-select-item')[1];
  if (secondOption) {
    fireEvent.click(secondOption);
  }

  expect(mockOnSelectChange).toHaveBeenCalledWith('Option 2');
});

test('Typing in the input filter should trigger a callback', async () => {
  render(
    <AdminHeader
      options={options}
      selectedValue="Option 1"
      onSelectChange={mockOnSelectChange}
      filterValue=""
      onFilterChange={mockOnFilterChange}
      placeholder="Filter data..."
    />
  );

  const inputFilter = screen.getByPlaceholderText('Filter data...');

  fireEvent.change(inputFilter, { target: { value: 'new filter' } });

  expect(mockOnFilterChange).toHaveBeenCalledWith('new filter');
});

test('renders configAddress correctly when passed as prop', () => {
  const configAddressValue = 'path/to/config';

  render(
    <AdminHeader
      options={options}
      selectedValue="Option 1"
      onSelectChange={mockOnSelectChange}
      filterValue=""
      onFilterChange={mockOnFilterChange}
      placeholder="Filter data..."
      configAddress={configAddressValue}
    />
  );

  expect(screen.getByText('Configuration files location:')).toBeInTheDocument();
  expect(screen.getByText(configAddressValue)).toBeInTheDocument();
});

test('does not render configAddress when not passed as prop', () => {
  render(
    <AdminHeader
      options={options}
      selectedValue="Option 1"
      onSelectChange={mockOnSelectChange}
      filterValue=""
      onFilterChange={mockOnFilterChange}
      placeholder="Filter data..."
    />
  );

  expect(screen.queryByText('Configuration files location:')).not.toBeInTheDocument();
});
