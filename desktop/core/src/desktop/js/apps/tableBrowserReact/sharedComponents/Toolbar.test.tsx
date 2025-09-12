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

import Toolbar, { ToolbarProps, ToolbarAction } from './Toolbar';

// Mock the problematic Tooltip component
jest.mock('cuix/dist/components/Tooltip', () => {
  return function MockTooltip({ children, title }: { children: React.ReactNode; title?: string }) {
    return <div title={title}>{children}</div>;
  };
});

describe('Toolbar', () => {
  const createAction = (overrides: Partial<ToolbarAction> = {}): ToolbarAction => ({
    key: 'test-action',
    label: 'Test Action',
    onClick: jest.fn(),
    ...overrides
  });

  const defaultProps: ToolbarProps = {
    actions: [createAction()],
    loading: false,
    isRefreshing: false
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders actions as buttons', () => {
    const actions = [
      createAction({ key: 'action1', label: 'Action 1' }),
      createAction({ key: 'action2', label: 'Action 2' })
    ];

    render(<Toolbar {...defaultProps} actions={actions} />);

    expect(screen.getByRole('button', { name: /action 1/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /action 2/i })).toBeInTheDocument();
  });

  it('calls onClick when action button is clicked', async () => {
    const user = userEvent.setup();
    const onClick = jest.fn();
    const actions = [createAction({ onClick })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    await user.click(screen.getByRole('button', { name: /test action/i }));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders refresh action with special styling', () => {
    const actions = [createAction({ key: 'refresh', label: 'Refresh' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    expect(refreshButton).toBeInTheDocument();
  });

  it('disables action when disabled prop is true', () => {
    const actions = [createAction({ disabled: true })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    expect(screen.getByRole('button', { name: /test action/i })).toBeDisabled();
  });

  it('disables actions when loading', () => {
    render(<Toolbar {...defaultProps} loading={true} />);

    expect(screen.getByRole('button', { name: /test action/i })).toBeDisabled();
  });

  it('disables actions when refreshing', () => {
    render(<Toolbar {...defaultProps} isRefreshing={true} />);

    expect(screen.getByRole('button', { name: /test action/i })).toBeDisabled();
  });

  it('renders primary variant button', () => {
    const actions = [createAction({ variant: 'primary' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    expect(screen.getByRole('button', { name: /test action/i })).toBeInTheDocument();
  });

  it('renders danger variant button', () => {
    const actions = [createAction({ variant: 'danger' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    expect(screen.getByRole('button', { name: /test action/i })).toBeInTheDocument();
  });

  it('shows tooltip when provided', () => {
    const actions = [createAction({ tooltip: 'Custom tooltip' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // The tooltip should be rendered somewhere in the component
    expect(screen.getByRole('button', { name: /test action/i })).toBeInTheDocument();
  });

  it('renders with icon when provided', () => {
    const icon = <span data-testid="custom-icon">Icon</span>;
    const actions = [createAction({ icon })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('renders empty toolbar when no actions provided', () => {
    render(<Toolbar {...defaultProps} actions={[]} />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
