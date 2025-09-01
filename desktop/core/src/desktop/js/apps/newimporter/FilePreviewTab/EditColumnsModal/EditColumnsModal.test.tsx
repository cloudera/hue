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

jest.mock('../../../../utils/hooks/useLoadData/useLoadData', () => {
  return jest.fn(() => ({
    data: ['STRING', 'INT', 'FLOAT'],
    loading: false,
    error: null
  }));
});

describe('EditColumnsModal', () => {
  const columns: Column[] = [
    { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
    { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
  ];
  const sample = { importerDataKey: 'row1', col1: 'val1', col2: 42 };

  it('should list existing modal columns as expected', () => {
    render(
      <EditColumnsModal
        isOpen={true}
        closeModal={jest.fn()}
        columns={columns}
        setColumns={jest.fn()}
        sample={sample}
        sqlDialect="hive"
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

  it('should call setColumns with modified data from the table when Done is clicked', async () => {
    const setColumns = jest.fn();
    const closeModal = jest.fn();
    render(
      <EditColumnsModal
        isOpen={true}
        closeModal={closeModal}
        columns={columns}
        setColumns={setColumns}
        sample={sample}
        sqlDialect="hive"
      />
    );

    const user = userEvent.setup();

    await waitFor(() => {
      expect(screen.getByDisplayValue('col1')).toBeInTheDocument();
    });

    const nameInput = screen.getByDisplayValue('col1');
    await user.clear(nameInput);
    await user.type(nameInput, 'newCol1');

    const commentTextarea = screen.getByDisplayValue('comment1');
    await user.clear(commentTextarea);
    await user.type(commentTextarea, 'new comment');

    const doneButton = screen.getByRole('button', { name: 'Done' });
    await user.click(doneButton);

    await waitFor(() => {
      expect(setColumns).toHaveBeenCalledWith([
        { ...columns[0], title: 'newCol1', type: 'STRING', comment: 'new comment' },
        { ...columns[1], type: 'INT' }
      ]);
      expect(closeModal).toHaveBeenCalled();
    });
  });

  it('should display SQL type options in select dropdown', async () => {
    render(
      <EditColumnsModal
        isOpen={true}
        closeModal={jest.fn()}
        columns={columns}
        setColumns={jest.fn()}
        sample={sample}
        sqlDialect="hive"
      />
    );

    await waitFor(() => {
      expect(screen.getByText('STRING')).toBeInTheDocument();
      expect(screen.getByText('INT')).toBeInTheDocument();
    });

    const typeSelectDivs = screen
      .getAllByLabelText('Column type')
      .filter(el => el.tagName === 'DIV');
    expect(typeSelectDivs).toHaveLength(2);
  });
});
