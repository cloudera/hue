import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import React from 'react';
import ReactExampleGlobal from './ReactExampleGlobal';

describe('ReactExampleGlobal', () => {
  // Make sure no unwanted console info are displayed during testing
  const consoleSpy = jest.spyOn(console, 'info').mockImplementation();

  afterEach(() => consoleSpy.mockClear());

  test('disables after click', () => {
    render(<ReactExampleGlobal />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Like me' });
    expect(btn).not.toBeDisabled();
    fireEvent.click(btn);
    expect(btn).toBeDisabled();
  });

  test('provides click callback', () => {
    const clickCallback = jest.fn();
    render(<ReactExampleGlobal onClick={clickCallback} />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Like me' });
    fireEvent.click(btn);
    expect(clickCallback).toHaveBeenCalled();
  });

  test('prints to console.info on click', () => {
    render(<ReactExampleGlobal version="1" myObj={{ id: 'a' }} />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Like me' });
    fireEvent.click(btn);
    expect(consoleSpy).toHaveBeenCalledWith('ReactExampleGlobal clicked  1 a');
  });
});
