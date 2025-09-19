// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import Privileges from './Privileges';

// Mock i18n
jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock CUIX EmptyState to avoid styled-components issues
jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title, subtitle }: any) => (
    <div>
      <div>{title}</div>
      <div>{subtitle}</div>
    </div>
  )
}));

// Mock API post using local factory; access via require()
jest.mock('../../../../api/utils', () => {
  return {
    __esModule: true,
    post: jest.fn()
  };
});

describe('Privileges', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows access empty state if database or table missing', () => {
    render(<Privileges />);
    expect(screen.getByText('You don’t have access')).toBeInTheDocument();
  });

  it('shows error state when request fails', async () => {
    const { post } = require('../../../../api/utils');
    post.mockRejectedValueOnce(new Error('boom'));
    render(<Privileges database="default" table="customers" />);
    expect(await screen.findByText('Failed to load privileges')).toBeInTheDocument();
  });

  it('shows empty state when no privileges returned', async () => {
    const { post } = require('../../../../api/utils');
    post.mockResolvedValueOnce({ status: 0, privileges: [] });
    render(<Privileges database="default" table="customers" />);
    await waitFor(() =>
      expect(screen.getByText('No permissions found')).toBeInTheDocument()
    );
  });

  it('renders privileges table when data present', async () => {
    const { post } = require('../../../../api/utils');
    post.mockResolvedValueOnce({
      status: 0,
      privileges: [
        {
          server: 's',
          database: 'default',
          table: 'customers',
          column: '',
          URI: '',
          action: 'SELECT',
          timestamp: 1700000000,
          roleName: 'role1',
          grantOption: true,
          scope: 'TABLE'
        }
      ]
    });
    render(<Privileges database="default" table="customers" />);

    // Expect header cells
    expect(await screen.findByText('Role')).toBeInTheDocument();
    // Expect one data row
    expect(screen.getByText('role1')).toBeInTheDocument();
    expect(screen.getByText('TABLE')).toBeInTheDocument();
    expect(screen.getByText('SELECT')).toBeInTheDocument();
    expect(screen.getByText('Yes')).toBeInTheDocument();
  });
});


