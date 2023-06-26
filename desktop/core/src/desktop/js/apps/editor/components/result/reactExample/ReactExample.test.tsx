import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import ReactExample from './ReactExample';

// For now, this is needed to mock cuix components exported as ESM (ECMAScript module)
jest.mock('cuix/dist/components/Button/PrimaryButton', () => () => undefined);
jest.mock('@cloudera/cuix-core/icons/react/PlusCircleIcon', () => () => undefined);

// Required by the antd Pagination component
window.matchMedia = jest.fn().mockImplementation(query => {
  return {
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // for older versions of Safari
    removeListener: jest.fn() // for older versions of Safari
  };
});

describe('ReactExample', () => {
  test('shows a title', () => {
    render(<ReactExample title="test title" />);
    const title = screen.getByText('test title');
    expect(title).toBeDefined();
  });
});
