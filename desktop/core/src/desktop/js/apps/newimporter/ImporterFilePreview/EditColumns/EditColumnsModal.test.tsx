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
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import EditColumnsModal, { Column } from './EditColumnsModal';
const EditColumnsModalWithLoading = require('./EditColumnsModal').default;
const EditColumnsModalWithError = require('./EditColumnsModal').default;

jest.mock(
  '../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper',
  () =>
    ({ children }: any) => <>{children}</>
);

jest.mock('../../../../utils/hooks/useLoadData/useLoadData', () => () => ({
  data: ['string', 'int', 'float'],
  loading: false,
  error: null
}));

describe('EditColumnsModal', () => {
  const columns: Column[] = [
    { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
    { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
  ];
  const sample = [{ col1: 'val1', col2: 42 }];

  test('lists existing modal columns as expected', async () => {
    render(
      <EditColumnsModal
        isOpen={true}
        closeModal={jest.fn()}
        columns={columns}
        setColumns={jest.fn()}
        sample={sample}
      />
    );

    expect(screen.getByTestId('modal')).toBeInTheDocument();

    expect(screen.getByDisplayValue('col1')).toBeInTheDocument();
    expect(screen.getByDisplayValue('col2')).toBeInTheDocument();
    expect(screen.getByDisplayValue('string')).toBeInTheDocument();
    expect(screen.getByDisplayValue('int')).toBeInTheDocument();
    expect(screen.getByDisplayValue('val1')).toBeInTheDocument();
    expect(screen.getByDisplayValue('42')).toBeInTheDocument();
    expect(screen.getByDisplayValue('comment1')).toBeInTheDocument();
    expect(screen.getByDisplayValue('comment2')).toBeInTheDocument();
  });

  test('Save should call setColumns with modified data from the table', async () => {
    const setColumns = jest.fn();
    const closeModal = jest.fn();
    render(
      <EditColumnsModal
        isOpen={true}
        closeModal={closeModal}
        columns={columns}
        setColumns={setColumns}
        sample={sample}
      />
    );

    const user = userEvent.setup();
    jest.mock(
      '../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper',
      () =>
        ({ children }: { children: React.ReactNode }) => <>{children}</>
    );

    jest.mock('../../../../utils/hooks/useLoadData/useLoadData', () => () => ({
      data: ['string', 'int', 'float'],
      loading: false,
      error: null
    }));

    describe('EditColumnsModal', () => {
      const columns: Column[] = [
        { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];
      const sample = [{ col1: 'val1', col2: 42 }];

      test('lists existing modal columns as expected', async () => {
        render(
          <EditColumnsModal
            isOpen={true}
            closeModal={jest.fn()}
            columns={columns}
            setColumns={jest.fn()}
            sample={sample}
          />
        );

        // Modal should be present
        expect(screen.getByTestId('modal')).toBeInTheDocument();

        // All fields should be present with correct values
        expect(screen.getByDisplayValue('col1')).toBeInTheDocument();
        expect(screen.getByDisplayValue('col2')).toBeInTheDocument();
        expect(screen.getByDisplayValue('string')).toBeInTheDocument();
        expect(screen.getByDisplayValue('int')).toBeInTheDocument();
        expect(screen.getByDisplayValue('val1')).toBeInTheDocument();
        expect(screen.getByDisplayValue('42')).toBeInTheDocument();
        expect(screen.getByDisplayValue('comment1')).toBeInTheDocument();
        expect(screen.getByDisplayValue('comment2')).toBeInTheDocument();
      });

      test('Save should call setColumns with modified data from the table', async () => {
        const setColumns = jest.fn();
        const closeModal = jest.fn();
        render(
          <EditColumnsModal
            isOpen={true}
            closeModal={closeModal}
            columns={columns}
            setColumns={setColumns}
            sample={sample}
          />
        );

        const user = userEvent.setup();

        // Change the name of the first column
        const nameInputs = screen.getAllByDisplayValue('col1');
        await user.clear(nameInputs[0]);
        await user.type(nameInputs[0], 'newCol1');

        // Change the type of the second column
        const typeSelects = screen.getAllByDisplayValue('int');
        await user.selectOptions(typeSelects[0], 'float');

        // Change the comment of the first column
        const commentInputs = screen.getAllByDisplayValue('comment1');
        await user.clear(commentInputs[0]);
        await user.type(commentInputs[0], 'new comment');

        // Click Done (ok) button
        const doneButton = screen.getByText('Done');
        await user.click(doneButton);

        await waitFor(() => {
          expect(setColumns).toHaveBeenCalledWith([
            { ...columns[0], title: 'newCol1', type: 'string', comment: 'new comment' },
            { ...columns[1], title: 'col2', type: 'float', comment: 'comment2' }
          ]);
          expect(closeModal).toHaveBeenCalled();
        });
      });

      test('should disable type select when sqlTypes are loading', () => {
        jest.resetModules();
        jest.doMock('../../../../utils/hooks/useLoadData/useLoadData', () => () => ({
          data: [],
          loading: true,
          error: null
        }));
        // Re-import after mocking

        render(
          <EditColumnsModalWithLoading
            isOpen={true}
            closeModal={jest.fn()}
            columns={columns}
            setColumns={jest.fn()}
            sample={sample}
          />
        );

        // All selects should be disabled
        const selects = screen.getAllByRole('combobox');
        selects.forEach(select => {
          expect(select).toBeDisabled();
        });
      });

      test('should show error message if sqlTypes fetch fails', () => {
        jest.resetModules();
        jest.doMock('../../../../utils/hooks/useLoadData/useLoadData', () => () => ({
          data: [],
          loading: false,
          error: new Error('Failed to fetch')
        }));

        render(
          <EditColumnsModalWithError
            isOpen={true}
            closeModal={jest.fn()}
            columns={columns}
            setColumns={jest.fn()}
            sample={sample}
          />
        );

        expect(screen.getByText('Failed to fetch SQL types.')).toBeInTheDocument();
      });

      test('should call closeModal when Cancel is clicked', async () => {
        const closeModal = jest.fn();
        render(
          <EditColumnsModal
            isOpen={true}
            closeModal={closeModal}
            columns={columns}
            setColumns={jest.fn()}
            sample={sample}
          />
        );
        const user = userEvent.setup();
        const cancelButton = screen.getByText('Cancel');
        await user.click(cancelButton);
        expect(closeModal).toHaveBeenCalled();
      });

      test('should update comment for the second column', async () => {
        const setColumns = jest.fn();
        const closeModal = jest.fn();
        render(
          <EditColumnsModal
            isOpen={true}
            closeModal={closeModal}
            columns={columns}
            setColumns={setColumns}
            sample={sample}
          />
        );
        const user = userEvent.setup();

        // Change the comment of the second column
        const commentInputs = screen.getAllByDisplayValue('comment2');
        await user.clear(commentInputs[0]);
        await user.type(commentInputs[0], 'updated comment2');

        // Click Done
        const doneButton = screen.getByText('Done');
        await user.click(doneButton);

        await waitFor(() => {
          expect(setColumns).toHaveBeenCalledWith([
            { ...columns[0], title: 'col1', type: 'string', comment: 'comment1' },
            { ...columns[1], title: 'col2', type: 'int', comment: 'updated comment2' }
          ]);
          expect(closeModal).toHaveBeenCalled();
        });
      });
    });
    const doneButton = screen.getByText('Done');
    await user.click(doneButton);

    await waitFor(() => {
      expect(setColumns).toHaveBeenCalledWith([
        { ...columns[0], title: 'newCol1', type: 'string', comment: 'new comment' },
        { ...columns[1], title: 'col2', type: 'float', comment: 'comment2' }
      ]);
      expect(closeModal).toHaveBeenCalled();
    });
  });
});
