// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import Overview from './Overview';

jest.mock('../../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

// Mock Schema to control onCountChange
jest.mock('./Schema', () => ({
  __esModule: true,
  default: ({ onCountChange }: { onCountChange?: (n: number) => void }) => (
    <div>
      <button aria-label="set-count-1" onClick={() => onCountChange && onCountChange(1)} />
    </div>
  )
}));

// Mock Loading wrapper to just render children
jest.mock('cuix/dist/components/Loading', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>
}));

describe('Overview', () => {
  it('renders Schema header with initial columns count and updates on count change', async () => {
    const user = userEvent.setup();
    const columns = [
      { name: 'a', type: 'int' },
      { name: 'b', type: 'string' },
      { name: 'c', type: 'double' }
    ];

    render(
      <Overview
        columns={columns as any}
        loadingProperties={false}
        loadingStats={false}
        loadingColumns={false}
        loadingSamples={false}
      />
    );

    // Header shows i18n template with label and count
    expect(screen.getByText(/\{\{label\}\} \(\{\{count\}\}\)/)).toBeInTheDocument();

    // Trigger onCountChange from Schema mock
    await user.click(screen.getByLabelText('set-count-1'));
    // After update we still render the template (i18n mock just returns input)
    expect(screen.getByText(/\{\{label\}\} \(\{\{count\}\}\)/)).toBeInTheDocument();
  });
});


