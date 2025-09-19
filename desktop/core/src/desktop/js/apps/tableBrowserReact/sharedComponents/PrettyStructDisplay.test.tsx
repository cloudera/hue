// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import PrettyStructDisplay from './PrettyStructDisplay';

jest.mock('../../../utils/i18nReact', () => ({
  __esModule: true,
  i18nReact: { useTranslation: () => ({ t: (s: string) => s }) }
}));

describe('PrettyStructDisplay', () => {
  it('renders formatted struct and colored type tokens', () => {
    const struct = 'struct<a:int,b:struct<c:string,d:decimal(10,2)>>';
    render(<PrettyStructDisplay structType={struct} indentSize={2} uppercaseTypes={true} />);

    const container = screen.getByLabelText('Struct type pretty print');
    expect(container).toBeInTheDocument();
    // Should include pretty-printed markers like angle brackets and newlines inside <code>
    const code = container.querySelector('code')!;
    expect(code.textContent).toContain('STRUCT');
    expect(code.textContent).toContain('<');
    expect(code.textContent).toContain('>');

    // Should include colored labels for detected type tokens
    const colored = container.querySelectorAll('.hue-pretty-type-label');
    expect(colored.length).toBeGreaterThan(0);
  });

  it('supports compact mode via CSS class', () => {
    render(<PrettyStructDisplay structType={'struct<a:int>'} compact={true} />);
    const root = screen.getByLabelText('Struct type pretty print');
    expect(root.className).toContain('hue-pretty-struct-display--compact');
  });

  it('renders fallback empty when structType is empty', () => {
    render(<PrettyStructDisplay structType={''} />);
    const code = screen.getByLabelText('Struct type pretty print').querySelector('code')!;
    // No content
    expect((code.textContent || '').trim().length).toBe(0);
  });
});
