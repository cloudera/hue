import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import CreateAndUploadAction from './CreateAndUploadAction';
import { CREATE_DIRECTORY_API_URL, CREATE_FILE_API_URL } from '../../../api';

const mockSave = jest.fn();
jest.mock('../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

jest.mock('../../../../../utils/huePubSub', () => ({
  __esModule: true,
  publish: jest.fn()
}));

describe('CreateAndUploadAction', () => {
  const currentPath = '/some/path';
  const onActionSuccess = jest.fn();
  const onActionError = jest.fn();
  const mockFilesUpload = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    render(
      <CreateAndUploadAction
        currentPath={currentPath}
        onActionSuccess={onActionSuccess}
        onFilesUpload={mockFilesUpload}
        onActionError={onActionError}
      />
    );
  });

  it('should render the dropdown with actions', async () => {
    const newButton = screen.getByRole('button', { name: 'New' });
    expect(newButton).toBeInTheDocument();

    await act(async () => fireEvent.click(newButton));

    // Check that the "Create" and "Upload" groups are in the dropdown
    expect(screen.getByText('CREATE')).toBeInTheDocument();
    expect(screen.getByText('UPLOAD')).toBeInTheDocument();
  });

  it('should open the folder creation modal when "New Folder" is clicked', async () => {
    const newButton = screen.getByRole('button', { name: 'New' });
    await act(async () => fireEvent.click(newButton));

    const newFolderButton = screen.getByRole('menuitem', { name: 'New Folder' });
    await act(async () => fireEvent.click(newFolderButton));

    expect(screen.getByRole('dialog', { name: 'Create Folder' })).toBeInTheDocument();
  });

  it('should open the file creation modal when "New File" is clicked', async () => {
    const newButton = screen.getByRole('button', { name: 'New' });
    await act(async () => fireEvent.click(newButton));

    const newFileButton = screen.getByRole('menuitem', { name: 'New File' });
    await act(async () => fireEvent.click(newFileButton));

    expect(screen.getByRole('dialog', { name: 'Create File' })).toBeInTheDocument();
  });

  it('should render hidden file input for upload functionality', async () => {
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('hidden');
    expect(fileInput).toHaveAttribute('multiple');
  });

  it('should handle file selection and call onFilesUpload', async () => {
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();

    const file1 = new File(['test content 1'], 'test1.txt', { type: 'text/plain' });
    const file2 = new File(['test content 2'], 'test2.txt', { type: 'text/plain' });

    fireEvent.change(fileInput!, {
      target: { files: [file1, file2] }
    });

    expect(mockFilesUpload).toHaveBeenCalledWith([file1, file2]);
  });

  it('should call the correct API for creating a folder', async () => {
    const newButton = screen.getByRole('button', { name: 'New' });
    await act(async () => fireEvent.click(newButton));

    const newFolderButton = screen.getByRole('menuitem', { name: 'New Folder' });
    await act(async () => fireEvent.click(newFolderButton));

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test Folder' } });

    const createButton = screen.getByRole('button', { name: 'Create' });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledWith(
        { path: currentPath, name: 'Test Folder' },
        { url: CREATE_DIRECTORY_API_URL }
      );
    });
  });

  it('should call the correct API for creating a file', async () => {
    const newButton = screen.getByRole('button', { name: 'New' });
    await act(async () => fireEvent.click(newButton));

    const newFileButton = screen.getByRole('menuitem', { name: 'New File' });
    await act(async () => fireEvent.click(newFileButton));

    // Simulate file name submission
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test File' } });

    const createButton = screen.getByRole('button', { name: 'Create' });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledWith(
        { path: currentPath, name: 'Test File' },
        { url: CREATE_FILE_API_URL }
      );
    });
  });
});
