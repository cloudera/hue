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

  it('renders actions dropdown button labeled "Actions" for multiple actions', () => {
    const actions = [
      createAction({ key: 'action1', label: 'Action 1' }),
      createAction({ key: 'action2', label: 'Action 2' })
    ];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Button should be labeled "Actions"
    expect(screen.getByRole('button', { name: /actions/i })).toBeInTheDocument();
    // Button should have dropdown trigger class
    expect(screen.getByRole('button')).toHaveClass('ant-dropdown-trigger');
  });

  it('renders multiple actions with primary variant as primary Actions button', () => {
    const actions = [
      createAction({ key: 'action1', label: 'Action 1', variant: 'primary' }),
      createAction({ key: 'action2', label: 'Action 2' })
    ];

    render(<Toolbar {...defaultProps} actions={actions} />);

    const button = screen.getByRole('button', { name: /actions/i });
    expect(button).toHaveClass('ant-btn-primary');
  });

  it('renders single action as regular button', () => {
    const actions = [createAction({ key: 'single', label: 'Single Action' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Single action should be rendered as regular button with its own label
    const button = screen.getByRole('button', { name: /single action/i });
    expect(button).toBeInTheDocument();
    expect(button).not.toHaveClass('ant-dropdown-trigger');
  });

  it('calls onClick when single action button is clicked', async () => {
    const user = userEvent.setup();
    const onClick = jest.fn();
    const actions = [createAction({ onClick })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Single action should be clickable directly
    await user.click(screen.getByRole('button', { name: /test action/i }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('disables single action button when action is disabled', () => {
    const actions = [createAction({ disabled: true })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Single disabled action should render as disabled button
    expect(screen.getByRole('button', { name: /test action/i })).toBeDisabled();
  });

  it('disables actions button when loading', () => {
    const actions = [
      createAction({ key: 'action1', label: 'Action 1' }),
      createAction({ key: 'action2', label: 'Action 2' })
    ];
    render(<Toolbar {...defaultProps} actions={actions} loading={true} />);

    expect(screen.getByRole('button', { name: /actions/i })).toBeDisabled();
  });

  it('disables actions button when refreshing', () => {
    const actions = [
      createAction({ key: 'action1', label: 'Action 1' }),
      createAction({ key: 'action2', label: 'Action 2' })
    ];
    render(<Toolbar {...defaultProps} actions={actions} isRefreshing={true} />);

    expect(screen.getByRole('button', { name: /actions/i })).toBeDisabled();
  });

  it('renders single primary action as primary button', () => {
    const actions = [createAction({ variant: 'primary' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    const button = screen.getByRole('button', { name: /test action/i });
    expect(button).toHaveClass('ant-btn-primary');
  });

  it('renders single danger action as danger button', () => {
    const actions = [createAction({ variant: 'danger' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Single danger action should be rendered as danger button
    const button = screen.getByRole('button', { name: /test action/i });
    expect(button).toHaveClass('ant-btn-dangerous');
  });

  it('renders single action button with tooltip', () => {
    const actions = [createAction({ tooltip: 'Custom tooltip' })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Single action with tooltip should be rendered as regular button
    expect(screen.getByRole('button', { name: /test action/i })).toBeInTheDocument();
  });

  it('renders single action button with icon', () => {
    const icon = <span data-testid="custom-icon">Icon</span>;
    const actions = [createAction({ icon })];

    render(<Toolbar {...defaultProps} actions={actions} />);

    // Single action with icon should be rendered as regular button with icon
    expect(screen.getByRole('button', { name: /test action/i })).toBeInTheDocument();
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('renders empty toolbar when no actions provided', () => {
    render(<Toolbar {...defaultProps} actions={[]} />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
