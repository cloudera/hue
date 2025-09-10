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

import ReactExampleGlobal from './ReactExampleGlobal';
import hueAnalytics from '../../utils/hueAnalytics';

describe('ReactExampleGlobal', () => {
  // Suppress console.info logs during all tests
  const originalConsoleInfo = console.info;

  beforeAll(() => {
    console.info = jest.fn();
  });

  afterAll(() => {
    console.info = originalConsoleInfo;
  });

  it('disables button after being clicked', async () => {
    const user = userEvent.setup();
    render(<ReactExampleGlobal />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    expect(btn).not.toBeDisabled();

    await user.click(btn);
    expect(btn).toBeDisabled();
  });

  it('calls provided onClick callback when clicked', async () => {
    const user = userEvent.setup();
    const clickCallback = jest.fn();
    render(<ReactExampleGlobal onClick={clickCallback} />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    await user.click(btn);
    expect(clickCallback).toHaveBeenCalled();
  });

  it('prints to console.info on click with provided props', async () => {
    const user = userEvent.setup();

    render(<ReactExampleGlobal version="1" myObj={{ id: 'a' }} />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    await user.click(btn);

    expect(console.info).toHaveBeenCalledWith('ReactExampleGlobal clicked  1 a');
  });

  it('handles undefined myObj gracefully', async () => {
    const user = userEvent.setup();

    render(<ReactExampleGlobal version="1" />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    await user.click(btn);

    expect(console.info).toHaveBeenCalledWith('ReactExampleGlobal clicked  1 undefined');
  });

  it('applies custom className when provided', () => {
    render(<ReactExampleGlobal className="custom-class" />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    expect(btn).toHaveClass('custom-class');
    expect(btn).toHaveClass('react-example-global'); // Should still have base class
  });

  it('renders custom children instead of default text', () => {
    render(<ReactExampleGlobal>Custom Text</ReactExampleGlobal>);
    expect(
      screen.getByRole('button', { name: 'ReactExampleGlobal - Custom Text' })
    ).toBeInTheDocument();
  });

  it('renders with default text when no children provided', () => {
    render(<ReactExampleGlobal />);
    expect(screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' })).toBeInTheDocument();
  });

  it('maintains disabled state after multiple clicks', async () => {
    const user = userEvent.setup();
    render(<ReactExampleGlobal />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });

    await user.click(btn);
    expect(btn).toBeDisabled();

    // Try clicking again - should remain disabled
    await user.click(btn);
    expect(btn).toBeDisabled();
  });

  it('logs analytics event on click', async () => {
    const analyticsSpy = jest.spyOn(hueAnalytics, 'log').mockImplementation();
    const user = userEvent.setup();

    render(<ReactExampleGlobal />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    await user.click(btn);

    expect(analyticsSpy).toHaveBeenCalledWith('test-area', 'button click', true);
    analyticsSpy.mockRestore();
  });
});
