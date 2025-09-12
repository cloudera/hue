// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import TableBrowserErrorBoundary from './TableBrowserErrorBoundary';

// Component that throws an error for testing
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('TableBrowserErrorBoundary', () => {
  // Suppress console.error during tests since we're intentionally throwing errors
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  afterAll(() => {
    console.error = originalError;
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children when no error occurs', () => {
    render(
      <TableBrowserErrorBoundary>
        <div>Child content</div>
      </TableBrowserErrorBoundary>
    );

    expect(screen.getByText('Child content')).toBeInTheDocument();
  });

  it('renders error UI when child component throws error', () => {
    render(
      <TableBrowserErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TableBrowserErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/an error occurred while loading/i)).toBeInTheDocument();
  });

  it('shows try again and refresh page buttons on error', () => {
    render(
      <TableBrowserErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TableBrowserErrorBoundary>
    );

    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /refresh page/i })).toBeInTheDocument();
  });

  it('calls onRetry when try again button is clicked', async () => {
    const user = userEvent.setup();
    const onRetry = jest.fn();

    render(
      <TableBrowserErrorBoundary onRetry={onRetry}>
        <ThrowError shouldThrow={true} />
      </TableBrowserErrorBoundary>
    );

    await user.click(screen.getByRole('button', { name: /try again/i }));

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('resets error state when try again is clicked', async () => {
    const user = userEvent.setup();

    const TestComponent = () => {
      const [shouldThrow, setShouldThrow] = React.useState(true);
      
      return (
        <TableBrowserErrorBoundary onRetry={() => setShouldThrow(false)}>
          <ThrowError shouldThrow={shouldThrow} />
        </TableBrowserErrorBoundary>
      );
    };

    render(<TestComponent />);

    // Initially shows error
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

    // Click try again
    await user.click(screen.getByRole('button', { name: /try again/i }));

    // Should show normal content
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    const customFallback = <div>Custom error message</div>;

    render(
      <TableBrowserErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </TableBrowserErrorBoundary>
    );

    expect(screen.getByText('Custom error message')).toBeInTheDocument();
    expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
  });

  it('does not call onRetry when not provided', async () => {
    const user = userEvent.setup();

    render(
      <TableBrowserErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TableBrowserErrorBoundary>
    );

    // Should not throw when clicking try again without onRetry
    await user.click(screen.getByRole('button', { name: /try again/i }));

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it('handles refresh page button click', async () => {
    const user = userEvent.setup();
    
    // Mock window.location.reload
    const mockReload = jest.fn();
    Object.defineProperty(window, 'location', {
      value: { reload: mockReload },
      writable: true
    });

    render(
      <TableBrowserErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TableBrowserErrorBoundary>
    );

    await user.click(screen.getByRole('button', { name: /refresh page/i }));

    expect(mockReload).toHaveBeenCalledTimes(1);
  });
});
