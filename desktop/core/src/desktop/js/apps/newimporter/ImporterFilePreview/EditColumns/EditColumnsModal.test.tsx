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

jest.mock('cuix/dist/components/Modal', () => {
  const Modal = ({ children, title, className, onOk, onCancel, okText, cancelText }: any) => (
    <div data-testid="modal" className={className}>
      <h2>{title}</h2>
      {children}
      <button onClick={onCancel}>{cancelText || 'Cancel'}</button>
      <button onClick={onOk}>{okText || 'Done'}</button>
    </div>
  );
  return Modal;
});
jest.mock('cuix/dist/components/Table', () => ({ columns, dataSource }: any) => (
  <table>
    <tbody>
      {dataSource.map((row: any, idx: number) => (
        <tr key={row.key}>
          {columns.map((col: any, colIdx: number) => (
            <td key={colIdx}>
              {col.render ? col.render(row[col.dataIndex], row, idx) : row[col.dataIndex]}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  </table>
));
jest.mock('cuix/dist/components/Input', () => (props: any) => <input {...props} />);
jest.mock('cuix/dist/components/Select', () => {
  const Select = ({ children, value, onChange, ...props }: any) => (
    <select {...props} value={value} onChange={e => onChange(e.target.value)}>
      {children}
    </select>
  );
  Select.Option = ({ children, ...props }: any) => <option {...props}>{children}</option>;
  return Select;
});
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

    // Change the name of the first column
    const nameInputs = screen.getAllByPlaceholderText('Column Name');
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
});
