// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrashActions from './TrashActions';

const mockSave = jest.fn();
jest.mock('../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

const mockOnActionSuccess = jest.fn();
const mockOnActionError = jest.fn();
const mockOnTrashEmptySuccess = jest.fn();
const mockSetLoadingFiles = jest.fn();

describe('TrashActions Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockSelectedFiles = [
    {
      name: 'file1.txt',
      size: '0 Byte',
      type: 'file',
      permission: 'rwxrwxrwx',
      mtime: '2021-01-01 00:00:00',
      path: '/user/path/.Trash/Current/file1.txt',
      user: 'test',
      group: 'test',
      replication: 1
    }
  ];

  const mockCurrentPath = '/user/path/.Trash/Current';
  const mockIsTrashEmpty = !mockSelectedFiles.length;

  it('should render the Restore and Empty trash buttons', () => {
    const { getByText } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    expect(getByText('Restore')).toBeInTheDocument();
    expect(getByText('Empty trash')).toBeInTheDocument();
  });

  it('should call onRestoreFiles when "Restore" button is clicked', async () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Restore' }));

    expect(mockSetLoadingFiles).toHaveBeenCalledWith(true);
    expect(mockSave).toHaveBeenCalled();
  });

  it('should call onTrashEmpty when "Empty trash" button is clicked', async () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Empty trash' }));

    expect(mockSetLoadingFiles).toHaveBeenCalledWith(true);
    expect(mockSave).toHaveBeenCalled();
  });

  it('should disable "Restore" button if no files are selected', () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={[]}
        currentPath={mockCurrentPath}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    expect(getByRole('button', { name: 'Restore' })).toBeDisabled();
  });

  it('should disable "Restore" button if current path is not restorable', () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={'path/not/restorable'}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    expect(getByRole('button', { name: 'Restore' })).toBeDisabled();
  });

  it('should disable "Empty trash" button if trash is empty', () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        isTrashEmpty={true}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    expect(getByRole('button', { name: 'Empty trash' })).toBeDisabled();
  });

  it('should call onActionError when restore fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnActionError(new Error('Restore failed'));
    });

    const { getByText } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByText('Restore'));

    expect(mockOnActionError).toHaveBeenCalledWith(new Error('Restore failed'));
  });

  it('should call onTrashEmptySuccess when trash is emptied successfully', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnTrashEmptySuccess();
    });

    const { getByText } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        isTrashEmpty={mockIsTrashEmpty}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        setLoadingFiles={mockSetLoadingFiles}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByText('Empty trash'));

    expect(mockOnTrashEmptySuccess).toHaveBeenCalledTimes(1);
  });
});
