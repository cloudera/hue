import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import ReactExampleGlobal from './ReactExampleGlobal';

describe('ReactExampleGlobal', () => {
  // Make sure no unwanted console info are displayed during testing
  const consoleSpy = jest.spyOn(console, 'info').mockImplementation();

  afterEach(() => consoleSpy.mockClear());

  test('disables after click', async () => {
    // It is recommended to call userEvent.setup per test
    const user = userEvent.setup();
    render(<ReactExampleGlobal />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    expect(btn).not.toBeDisabled();

    await user.click(btn);
    expect(btn).toBeDisabled();
  });

  test('provides click callback', async () => {
    const user = userEvent.setup();
    const clickCallback = jest.fn();
    render(<ReactExampleGlobal onClick={clickCallback} />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    await user.click(btn);
    expect(clickCallback).toHaveBeenCalled();
  });

  test('prints to console.info on click', async () => {
    const user = userEvent.setup();
    render(<ReactExampleGlobal version="1" myObj={{ id: 'a' }} />);
    const btn = screen.getByRole('button', { name: 'ReactExampleGlobal - Yes' });
    await user.click(btn);
    expect(consoleSpy).toHaveBeenCalledWith('ReactExampleGlobal clicked  1 a');
  });
});
