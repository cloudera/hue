import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import CreateAndUploadAction from './CreateAndUploadAction';
import {
  CREATE_DIRECTORY_API_URL,
  CREATE_FILE_API_URL
} from '../../../../reactComponents/FileChooser/api';

const mockSave = jest.fn();
jest.mock('../../../../utils/hooks/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

jest.mock('../../../../utils/huePubSub', () => ({
  __esModule: true,
  publish: jest.fn()
}));

describe('CreateAndUploadAction', () => {
  const currentPath = '/some/path';
  const onSuccessfulAction = jest.fn();
  const setLoadingFiles = jest.fn();

  beforeEach(() => {
    render(
      <CreateAndUploadAction
        currentPath={currentPath}
        onSuccessfulAction={onSuccessfulAction}
        setLoadingFiles={setLoadingFiles}
      />
    );
  });

  it('should render the dropdown with actions', async () => {
    const newButton = screen.getByText('New');
    expect(newButton).toBeInTheDocument();

    await act(async () => fireEvent.click(newButton));

    // Check that the "Create" and "Upload" groups are in the dropdown
    expect(screen.getByText('CREATE')).toBeInTheDocument();
    expect(screen.getByText('UPLOAD')).toBeInTheDocument();
  });

  it('should open the folder creation modal when "New Folder" is clicked', async () => {
    const newButton = screen.getByText('New');
    await act(async () => fireEvent.click(newButton));

    const newFolderButton = screen.getByText('New Folder');
    await act(async () => fireEvent.click(newFolderButton));

    expect(screen.getByText('Create New Folder')).toBeInTheDocument();
  });

  it('should open the file creation modal when "New File" is clicked', async () => {
    const newButton = screen.getByText('New');
    await act(async () => fireEvent.click(newButton));

    const newFileButton = screen.getByText('New File');
    await act(async () => fireEvent.click(newFileButton));

    expect(screen.getByText('Create New File')).toBeInTheDocument();
  });

  it('should open the upload file modal when "New Upload" is clicked', async () => {
    const newButton = screen.getByText('New');
    await act(async () => fireEvent.click(newButton));

    const newUploadButton = screen.getByText('New Upload');
    fireEvent.click(newUploadButton);

    // Check if the upload modal is opened
    expect(screen.getByText('Upload A File')).toBeInTheDocument();
  });

  it('should call the correct API for creating a folder', async () => {
    const newButton = screen.getByText('New');
    await act(async () => fireEvent.click(newButton));

    const newFolderButton = screen.getByText('New Folder');
    await act(async () => fireEvent.click(newFolderButton));

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test Folder' } });

    const createButton = screen.getByText('Create');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledWith(
        { path: currentPath, name: 'Test Folder' },
        { url: CREATE_DIRECTORY_API_URL } // This URL is assumed from the code.
      );
    });
  });

  it('should call the correct API for creating a file', async () => {
    const newButton = screen.getByText('New');
    await act(async () => fireEvent.click(newButton));

    const newFileButton = screen.getByText('New File');
    await act(async () => fireEvent.click(newFileButton));

    // Simulate file name submission
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test File' } });

    const createButton = screen.getByText('Create');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledWith(
        { path: currentPath, name: 'Test File' },
        { url: CREATE_FILE_API_URL } // This URL is assumed from the code.
      );
    });
  });
});
