import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import ReactExample from './ReactExample';

describe('ReactExample', () => {
  test('shows a title', () => {
    render(<ReactExample title="test title" />);
    const title = screen.getByText('test title');
    expect(title).toBeDefined();
  });
});
