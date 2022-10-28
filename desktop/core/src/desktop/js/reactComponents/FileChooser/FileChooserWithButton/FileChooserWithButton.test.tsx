import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import React from 'react';

import FileChooserWithButton from './FileChooserWithButton';

test('Filechooser modal opens on button click', async () => {
  const user = userEvent.setup();
  const { queryByText } = render(<FileChooserWithButton title={'File chooser component'} />);
  await user.click(screen.getByRole('button', { name: 'File chooser component' }));
  expect(queryByText('Choose a file')).toBeInTheDocument();
});
