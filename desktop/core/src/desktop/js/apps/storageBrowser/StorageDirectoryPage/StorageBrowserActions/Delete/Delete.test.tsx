import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeleteAction from './Delete';
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import {
  BULK_DELETION_API_URL,
  DELETION_API_URL
} from '../../../../../reactComponents/FileChooser/api';

const mockFiles: StorageDirectoryTableData[] = [
  {
    name: 'file1.txt',
    size: '0 Byte',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: 'test/path/file1.txt',
    user: 'test',
    group: 'test',
    replication: 1
  },
  {
    name: 'file2.txt',
    size: '0 Byte',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: 'test/path/file2.txt',
    user: 'test',
    group: 'test',
    replication: 1
  }
];

const mockSave = jest.fn();
jest.mock('../../../../../utils/hooks/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: false
  }))
}));

describe('DeleteAction Component', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();
  const setLoading = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the Delete modal with the correct title and buttons', () => {
    const { getByText, getByRole } = render(
      <DeleteAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    expect(getByText('Delete file')).toBeInTheDocument();
    expect(getByText('Move to Trash')).toBeInTheDocument();
    expect(getByText('Delete Permanently')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('should render the Delete modal with the correct title and buttons when trash is not enabled', () => {
    const { getByText, queryByText, getByRole } = render(
      <DeleteAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={false}
      />
    );

    expect(getByText('Delete file')).toBeInTheDocument();
    expect(queryByText('Move to Trash')).not.toBeInTheDocument();
    expect(getByText('Delete Permanently')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('should call handleDeletion with the correct data for single delete when "Delete Permanently" is clicked', async () => {
    const { getByText } = render(
      <DeleteAction
        isOpen={true}
        files={[mockFiles[0]]}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={false}
      />
    );

    fireEvent.click(getByText('Delete Permanently'));

    const payload = { path: mockFiles[0].path, skip_trash: true };
    expect(mockSave).toHaveBeenCalledWith(payload, { url: DELETION_API_URL });
  });

  it('should call handleDeletion with the correct data for bulk delete when "Delete Permanently" is clicked', async () => {
    const { getByText } = render(
      <DeleteAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={false}
      />
    );

    fireEvent.click(getByText('Delete Permanently'));

    const formData = new FormData();
    mockFiles.forEach(file => {
      formData.append('path', file.path);
    });
    formData.append('skip_trash', 'true');

    expect(mockSave).toHaveBeenCalledWith(formData, { url: BULK_DELETION_API_URL });
  });

  it('should call handleDeletion with the correct data for trash delete when "Move to Trash" is clicked', async () => {
    const { getByText } = render(
      <DeleteAction
        isOpen={true}
        files={[mockFiles[0]]}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Move to Trash'));

    const payload = { path: mockFiles[0].path };
    expect(mockSave).toHaveBeenCalledWith(payload, { url: DELETION_API_URL });
  });

  it('should call handleDeletion with the correct data for bulk trash delete when "Move to Trash" is clicked', async () => {
    const { getByText } = render(
      <DeleteAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Move to Trash'));

    const formData = new FormData();
    mockFiles.forEach(file => {
      formData.append('path', file.path);
    });

    expect(mockSave).toHaveBeenCalledWith(formData, { url: BULK_DELETION_API_URL });
  });

  it('should call onError when the delete request fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error());
    });
    const { getByText } = render(
      <DeleteAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Move to Trash'));

    expect(mockOnError).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when the modal is closed', () => {
    const { getByText } = render(
      <DeleteAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Cancel'));

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
