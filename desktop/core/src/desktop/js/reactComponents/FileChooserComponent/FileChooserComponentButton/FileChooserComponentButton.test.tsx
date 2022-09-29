import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import FileChooserComponentButton from './FileChooserComponentButton';

test('Filechooser modal opens on button click', async () => {
  const { queryByText } = render(<FileChooserComponentButton />);
  fireEvent.click(queryByText('File chooser component'));
  await waitFor(() => expect(queryByText('Choose a file')).toBeInTheDocument());
});
