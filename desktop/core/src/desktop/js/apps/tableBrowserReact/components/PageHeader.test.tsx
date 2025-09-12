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

import PageHeader, { PageHeaderProps } from './PageHeader';

// Mock only the Breadcrumbs component (internal dependency)
jest.mock('./Breadcrumbs', () => {
  return function MockBreadcrumbs(props: {
    sourceType?: string;
    database?: string;
    table?: string;
  }) {
    return (
      <div data-testid="breadcrumbs">
        {props.sourceType && <span data-testid="breadcrumbs-source">{props.sourceType}</span>}
        {props.database && <span data-testid="breadcrumbs-database">{props.database}</span>}
        {props.table && <span data-testid="breadcrumbs-table">{props.table}</span>}
      </div>
    );
  };
});

describe('PageHeader', () => {
  const defaultProps: PageHeaderProps = {
    title: 'Test Title',
    onRefresh: jest.fn(),
    loading: false,
    isRefreshing: false
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with title', () => {
    render(<PageHeader {...defaultProps} />);

    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Test Title');
  });

  it('renders with title and icon', () => {
    const icon = <span data-testid="test-icon">TestIcon</span>;
    render(<PageHeader {...defaultProps} icon={icon} />);

    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Test Title');
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  it('renders refresh button when onRefresh is provided', () => {
    render(<PageHeader {...defaultProps} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    expect(refreshButton).toBeInTheDocument();
  });

  it('does not render refresh button when onRefresh is not provided', () => {
    render(<PageHeader {...defaultProps} onRefresh={undefined} />);

    expect(screen.queryByRole('button', { name: /refresh/i })).not.toBeInTheDocument();
  });

  it('calls onRefresh when refresh button is clicked', async () => {
    const user = userEvent.setup();
    const onRefresh = jest.fn();

    render(<PageHeader {...defaultProps} onRefresh={onRefresh} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    await user.click(refreshButton);

    expect(onRefresh).toHaveBeenCalledTimes(1);
  });

  it('disables refresh button when loading', () => {
    render(<PageHeader {...defaultProps} loading={true} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    expect(refreshButton).toBeDisabled();
  });

  it('disables refresh button when refreshing', () => {
    render(<PageHeader {...defaultProps} isRefreshing={true} />);

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    expect(refreshButton).toBeDisabled();
  });

  it('renders breadcrumbs when sourceType is provided', () => {
    render(<PageHeader {...defaultProps} sourceType="hive" />);

    const breadcrumbs = screen.getByTestId('breadcrumbs');
    expect(breadcrumbs).toBeInTheDocument();
    expect(screen.getByTestId('breadcrumbs-source')).toHaveTextContent('hive');
  });

  it('renders breadcrumbs when database is provided', () => {
    render(<PageHeader {...defaultProps} database="test_db" />);

    const breadcrumbs = screen.getByTestId('breadcrumbs');
    expect(breadcrumbs).toBeInTheDocument();
    expect(screen.getByTestId('breadcrumbs-database')).toHaveTextContent('test_db');
  });

  it('renders breadcrumbs when table is provided', () => {
    render(<PageHeader {...defaultProps} table="test_table" />);

    const breadcrumbs = screen.getByTestId('breadcrumbs');
    expect(breadcrumbs).toBeInTheDocument();
    expect(screen.getByTestId('breadcrumbs-table')).toHaveTextContent('test_table');
  });

  it('does not render breadcrumbs when no breadcrumb data is provided', () => {
    render(<PageHeader {...defaultProps} />);

    expect(screen.queryByTestId('breadcrumbs')).not.toBeInTheDocument();
  });

  it('returns null when no title and no breadcrumb data', () => {
    const { container } = render(
      <PageHeader title={undefined} sourceType={undefined} database={undefined} table={undefined} />
    );

    expect(container.firstChild).toBeNull();
  });

  it('renders only breadcrumbs without title', () => {
    render(<PageHeader title={undefined} sourceType="hive" onRefresh={jest.fn()} />);

    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    expect(screen.getByTestId('breadcrumbs')).toBeInTheDocument();
  });
});
