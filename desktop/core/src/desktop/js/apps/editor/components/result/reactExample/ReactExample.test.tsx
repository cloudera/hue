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
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Mock useLoadData hook to prevent actual API calls
jest.mock('../../../../../utils/hooks/useLoadData/useLoadData');

import ReactExample from './ReactExample';

// Required by the antd Pagination component
window.matchMedia = jest.fn().mockImplementation(query => {
  return {
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // for older versions of Safari
    removeListener: jest.fn() // for older versions of Safari
  };
});

// NOTE! This is an example file and will not test all the code.
// It is only used to show how to test a component.
describe('ReactExample', () => {
  it('opens modal when button is clicked', async () => {
    const user = userEvent.setup();
    render(<ReactExample />);

    await user.click(screen.getByRole('button', { name: 'Open Modal' }));

    // Test that modal is open and visible by checking for modal dialog role
    const modal = screen.getByRole('dialog');
    expect(modal).toBeVisible();

    // Test that modal can be closed
    await user.click(screen.getByRole('button', { name: 'OK' }));
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('shows a title', () => {
    render(<ReactExample title="test title" />);
    const title = screen.getByRole('heading', { name: 'test title' });
    expect(title).toBeVisible();
  });

  it('shows default title when no title prop provided', () => {
    render(<ReactExample />);
    // The default title comes from i18n, so we check for the component structure
    expect(screen.getByRole('heading', { level: 1 })).toBeVisible();
  });

  it('renders primary button', () => {
    render(<ReactExample />);
    expect(screen.getByRole('button', { name: 'Open Modal' })).toBeVisible();
  });

  it('renders history section', () => {
    render(<ReactExample />);
    expect(
      screen.getByRole('heading', {
        name: 'Editor History (useLoadData + LoadingErrorWrapper example)'
      })
    ).toBeVisible();
  });
});
