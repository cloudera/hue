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

  it('should render the Restore and Empty trash buttons', () => {
    const { getByRole, queryByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    expect(getByRole('button', { name: 'Restore' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'Empty trash' })).toBeInTheDocument();
    expect(queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('should open modal when "Restore" button is clicked', () => {
    const { getByText, getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Restore' }));

    expect(getByRole('dialog')).toBeInTheDocument();
    expect(getByText('Are you sure you want to restore these files?')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Yes' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'No' })).toBeInTheDocument();
  });

  it('should open modal when "Empty trash" button is clicked', () => {
    const { getByText, getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Empty trash' }));

    expect(getByRole('dialog')).toBeInTheDocument();
    expect(
      getByText('Are you sure you want to permanently delete all your trash?')
    ).toBeInTheDocument();
    expect(getByRole('button', { name: 'Yes' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'No' })).toBeInTheDocument();
  });

  it('should restore files when "Yes" is clicked in the modal for restore', () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Restore' }));
    fireEvent.click(getByRole('button', { name: 'Yes' }));

    expect(mockSave).toHaveBeenCalled();
  });

  it('should call onTrashEmpty when "Yes" is clicked in the modal for empty trash', () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Empty trash' }));
    fireEvent.click(getByRole('button', { name: 'Yes' }));

    expect(mockSave).toHaveBeenCalled();
  });

  it('should close modal when "No" is clicked', () => {
    const { getByRole, queryByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Restore' }));
    fireEvent.click(getByRole('button', { name: 'No' }));

    expect(queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('should disable "Restore" button if no files are selected', () => {
    const { getByRole } = render(
      <TrashActions
        selectedFiles={[]}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
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
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    expect(getByRole('button', { name: 'Restore' })).toBeDisabled();
  });

  it('should call onActionError when restore fails', () => {
    mockSave.mockImplementationOnce(() => {
      mockOnActionError(new Error('Restore failed'));
    });

    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Restore' }));
    fireEvent.click(getByRole('button', { name: 'Yes' }));

    expect(mockOnActionError).toHaveBeenCalledWith(new Error('Restore failed'));
  });

  it('should call onTrashEmptySuccess when trash is emptied successfully', () => {
    mockSave.mockImplementationOnce(() => {
      mockOnTrashEmptySuccess();
    });

    const { getByRole } = render(
      <TrashActions
        selectedFiles={mockSelectedFiles}
        currentPath={mockCurrentPath}
        onActionSuccess={mockOnActionSuccess}
        onActionError={mockOnActionError}
        onTrashEmptySuccess={mockOnTrashEmptySuccess}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Empty trash' }));
    fireEvent.click(getByRole('button', { name: 'Yes' }));

    expect(mockOnTrashEmptySuccess).toHaveBeenCalledTimes(1);
  });
});
