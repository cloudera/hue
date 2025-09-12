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

import Tabs, { TabsProps, TabKey } from './Tabs';

describe('Tabs', () => {
  const defaultProps: TabsProps = {
    activeKey: 'overview' as TabKey,
    onChange: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with overview tab active by default', () => {
    render(<Tabs {...defaultProps} />);

    const tabList = screen.getByRole('tablist');
    expect(tabList).toBeInTheDocument();
    
    expect(screen.getByRole('tab', { name: /overview/i })).toHaveAttribute('aria-selected', 'true');
  });

  it('calls onChange when different tab is clicked', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    render(<Tabs {...defaultProps} onChange={onChange} />);

    await user.click(screen.getByRole('tab', { name: /details/i }));

    expect(onChange).toHaveBeenCalledWith('details');
  });

  it('shows sample count when provided', () => {
    render(<Tabs {...defaultProps} sampleCount={150} />);

    expect(screen.getByRole('tab', { name: /sample \(150\)/i })).toBeInTheDocument();
  });

  it('shows partitions count when provided', () => {
    render(<Tabs {...defaultProps} partitionsCount={5} />);

    expect(screen.getByRole('tab', { name: /partitions \(5\)/i })).toBeInTheDocument();
  });

  it('shows queries tab when showQueries is true', () => {
    render(<Tabs {...defaultProps} showQueries={true} />);

    expect(screen.getByRole('tab', { name: /queries/i })).toBeInTheDocument();
  });

  it('hides queries tab when showQueries is false', () => {
    render(<Tabs {...defaultProps} showQueries={false} />);

    expect(screen.queryByRole('tab', { name: /queries/i })).not.toBeInTheDocument();
  });

  it('shows view sql tab when showViewSql is true', () => {
    render(<Tabs {...defaultProps} showViewSql={true} />);

    expect(screen.getByRole('tab', { name: /view sql/i })).toBeInTheDocument();
  });

  it('hides view sql tab when showViewSql is false', () => {
    render(<Tabs {...defaultProps} showViewSql={false} />);

    expect(screen.queryByRole('tab', { name: /view sql/i })).not.toBeInTheDocument();
  });

  it('shows erd tab when showErd is true', () => {
    render(<Tabs {...defaultProps} showErd={true} />);

    expect(screen.getByRole('tab', { name: /erd/i })).toBeInTheDocument();
  });

  it('hides erd tab when showErd is false', () => {
    render(<Tabs {...defaultProps} showErd={false} />);

    expect(screen.queryByRole('tab', { name: /erd/i })).not.toBeInTheDocument();
  });

  it('renders all default tabs when no conditional props provided', () => {
    render(<Tabs {...defaultProps} />);

    expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /sample/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /partitions/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /details/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /privileges/i })).toBeInTheDocument();
  });

  it('renders with different active tab', () => {
    render(<Tabs {...defaultProps} activeKey="sample" />);

    expect(screen.getByRole('tab', { name: /sample/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: /overview/i })).toHaveAttribute('aria-selected', 'false');
  });
});
