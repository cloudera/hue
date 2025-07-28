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

jest.mock('../../../../utils/hooks/useLoadData/useLoadData', () => () => ({
  data: ['STRING', 'INT', 'FLOAT'],
  loading: false,
  error: null
}));

describe('EditColumnsModal', () => {
  const columns: Column[] = [
    { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
    { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
  ];
  const sample = { importerDataKey: 'row1', col1: 'val1', col2: 42 };

  test('lists existing modal columns as expected', () => {
    render(
      <EditColumnsModal
        isOpen={true}
        closeModal={jest.fn()}
        columns={columns}
        setColumns={jest.fn()}
        sample={sample}
      />
    );

    expect(screen.getByDisplayValue('col1')).toBeInTheDocument();
    expect(screen.getByDisplayValue('col2')).toBeInTheDocument();

    expect(screen.getByText('STRING')).toBeInTheDocument();
    expect(screen.getByText('INT')).toBeInTheDocument();

    expect(screen.getByText('val1')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
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

    const nameInputs = screen.getAllByDisplayValue('col1');
    await user.clear(nameInputs[0]);
    await user.type(nameInputs[0], 'newCol1');

    const typeSelects = screen.getAllByText('STRING').map(el => el.closest('.ant-select'));
    if (typeSelects[0]) {
      await user.click(typeSelects[0].querySelector('.ant-select-selector')!);

      const floatOption = await screen.findByTitle('FLOAT');
      await user.click(floatOption);
    }

    const commentInputs = screen.getAllByDisplayValue('comment1');
    await user.clear(commentInputs[0]);
    await user.type(commentInputs[0], 'new comment');

    const doneButton = screen.getByText('Done');
    await user.click(doneButton);

    await waitFor(() => {
      expect(setColumns).toHaveBeenCalledWith([
        { ...columns[0], title: 'newCol1', type: 'FLOAT', comment: 'new comment' },
        { ...columns[1], title: 'col2', type: 'INT', comment: 'comment2' }
      ]);
      expect(closeModal).toHaveBeenCalled();
    });
  });
});
