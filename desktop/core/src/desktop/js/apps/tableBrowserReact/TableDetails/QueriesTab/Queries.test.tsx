// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import Queries from './Queries';

// Mock i18n
jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock cuix components
jest.mock('cuix/dist/components/EmptyState', () => ({
  __esModule: true,
  default: ({ title, subtitle }: any) => (
    <div>
      <div>{title}</div>
      <div>{subtitle}</div>
    </div>
  )
}));
jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: any) => <>{children}</>
}));

// Mock dataCatalog with local factory and access via require()
jest.mock('../../../../catalog/dataCatalog', () => {
  const mock = { getEntry: jest.fn() };
  return { __esModule: true, default: mock };
});

describe('Queries tab', () => {
  const connector = { id: 'hive', type: 'hive' } as any;
  const namespace = { id: 'ns' } as any;
  const compute = { id: 'cm' } as any;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows empty state when inputs are missing', () => {
    render(<Queries />);
    expect(screen.getByText('No related queries yet')).toBeInTheDocument();
  });

  it('shows empty state when analysis has no joins', async () => {
    const dataCatalog = require('../../../../catalog/dataCatalog').default;
    dataCatalog.getEntry.mockResolvedValueOnce({
      getAnalysis: jest.fn().mockResolvedValue({ top_joins: [] })
    });
    render(
      <Queries
        connector={connector}
        namespace={namespace}
        compute={compute}
        database="default"
        table="customers"
      />
    );
    expect(await screen.findByText('No related queries yet')).toBeInTheDocument();
  });

  it('renders a list of join expressions when available', async () => {
    const dataCatalog = require('../../../../catalog/dataCatalog').default;
    dataCatalog.getEntry.mockResolvedValueOnce({
      getAnalysis: jest.fn().mockResolvedValue({
        top_joins: [{ leftTable: 'a', leftColumn: 'id', rightTable: 'b', rightColumn: 'id' }]
      })
    });
    render(
      <Queries
        connector={connector}
        namespace={namespace}
        compute={compute}
        database="default"
        table="customers"
      />
    );
    expect(await screen.findByText('a.id = b.id')).toBeInTheDocument();
  });
});
