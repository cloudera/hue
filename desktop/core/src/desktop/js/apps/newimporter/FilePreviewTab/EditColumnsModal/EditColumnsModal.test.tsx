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
import { render, screen, waitFor, RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import EditColumnsModal, { Column } from './EditColumnsModal';

interface MockLoadDataReturn {
  data: string[] | null;
  loading: boolean;
  error: Error | null;
}

const mockUseLoadData = jest.fn<MockLoadDataReturn, []>();

jest.mock('../../../../utils/hooks/useLoadData/useLoadData', () => {
  return jest.fn().mockImplementation(() => mockUseLoadData());
});

jest.mock('../../../../utils/i18nReact', () => ({
  i18nReact: {
    useTranslation: () => ({
      t: (key: string, params?: Record<string, unknown>) => {
        if (params) {
          return Object.entries(params).reduce((str, [param, value]) => {
            return str.replace(new RegExp(`{{${param}}}`, 'g'), String(value));
          }, key);
        }
        return key;
      },
      ready: true
    })
  }
}));

describe('EditColumnsModal', () => {
  const DEFAULT_COLUMNS: Column[] = [
    { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
    { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
  ];

  const DEFAULT_SAMPLE = { importerDataKey: 'row1', col1: 'val1', col2: 42 };

  const DEFAULT_SQL_TYPES = ['STRING', 'INT', 'FLOAT'];

  const MOCK_STATES = {
    success: {
      data: DEFAULT_SQL_TYPES,
      loading: false,
      error: null
    },
    loading: {
      data: null,
      loading: true,
      error: null
    },
    error: {
      data: null,
      loading: false,
      error: new Error('Failed to fetch SQL types')
    },
    empty: {
      data: [] as string[],
      loading: false,
      error: null
    },
    invalidData: {
      data: 'invalid-string-data' as unknown as string[],
      loading: false,
      error: null
    }
  };

  interface RenderModalOptions {
    columns?: Column[];
    sample?: typeof DEFAULT_SAMPLE;
    sqlDialect?: string;
    setColumns?: jest.Mock;
    closeModal?: jest.Mock;
  }

  const renderModal = ({
    columns = DEFAULT_COLUMNS,
    sample = DEFAULT_SAMPLE,
    sqlDialect = 'hive',
    setColumns = jest.fn(),
    closeModal = jest.fn()
  }: RenderModalOptions = {}): RenderResult & { setColumns: jest.Mock; closeModal: jest.Mock } => {
    const result = render(
      <EditColumnsModal
        isOpen={true}
        closeModal={closeModal}
        columns={columns}
        setColumns={setColumns}
        sample={sample}
        sqlDialect={sqlDialect}
      />
    );

    return { ...result, setColumns, closeModal };
  };

  const getColumnTypeSelects = () =>
    screen.getAllByLabelText('Column type').filter(el => el.tagName === 'DIV');

  beforeEach(() => {
    mockUseLoadData.mockReturnValue(MOCK_STATES.success);
  });

  describe('Basic functionality', () => {
    it('should list existing modal columns as expected', () => {
      renderModal();

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
      const { setColumns, closeModal } = renderModal();
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
          {
            ...DEFAULT_COLUMNS[0],
            title: 'newCol1',
            type: 'STRING',
            comment: 'new comment',
            isPrimaryKey: false
          },
          { ...DEFAULT_COLUMNS[1], type: 'INT', isPrimaryKey: false }
        ]);
        expect(closeModal).toHaveBeenCalled();
      });
    });

    it('should display SQL type options in select dropdown', async () => {
      renderModal();

      await waitFor(() => {
        expect(screen.getByText('STRING')).toBeInTheDocument();
        expect(screen.getByText('INT')).toBeInTheDocument();
      });

      const typeSelects = getColumnTypeSelects();
      expect(typeSelects).toHaveLength(2);
    });

    it('should set isPrimaryKey to true when primary key checkbox is clicked', async () => {
      const { setColumns, closeModal } = renderModal();
      const user = userEvent.setup();

      await waitFor(() => {
        expect(screen.getByDisplayValue('col1')).toBeInTheDocument();
      });

      const primaryKeyCheckboxes = screen.getAllByLabelText('Set as primary key');
      expect(primaryKeyCheckboxes).toHaveLength(2);
      await user.click(primaryKeyCheckboxes[0]);

      const doneButton = screen.getByRole('button', { name: 'Done' });
      await user.click(doneButton);

      await waitFor(() => {
        expect(setColumns).toHaveBeenCalledWith([
          {
            ...DEFAULT_COLUMNS[0],
            type: 'STRING',
            comment: 'comment1',
            isPrimaryKey: true
          },
          { ...DEFAULT_COLUMNS[1], type: 'INT', comment: 'comment2', isPrimaryKey: false }
        ]);
        expect(closeModal).toHaveBeenCalled();
      });
    });

    it('should ensure only one column can be primary key at a time', async () => {
      const { setColumns, closeModal } = renderModal();
      const user = userEvent.setup();

      await waitFor(() => {
        expect(screen.getByDisplayValue('col1')).toBeInTheDocument();
      });

      const primaryKeyCheckboxes = screen.getAllByLabelText('Set as primary key');

      await user.click(primaryKeyCheckboxes[0]);
      await user.click(primaryKeyCheckboxes[1]);

      const doneButton = screen.getByRole('button', { name: 'Done' });
      await user.click(doneButton);

      await waitFor(() => {
        expect(setColumns).toHaveBeenCalledWith([
          {
            ...DEFAULT_COLUMNS[0],
            type: 'STRING',
            comment: 'comment1',
            isPrimaryKey: false
          },
          {
            ...DEFAULT_COLUMNS[1],
            type: 'INT',
            comment: 'comment2',
            isPrimaryKey: true
          }
        ]);
        expect(closeModal).toHaveBeenCalled();
      });
    });
  });

  describe('Edge cases with column data', () => {
    it('should handle empty columns array', () => {
      renderModal({ columns: [] });

      expect(screen.getByText('Edit Columns')).toBeInTheDocument();
      expect(screen.queryByDisplayValue('col1')).not.toBeInTheDocument();
      expect(screen.queryByDisplayValue('col2')).not.toBeInTheDocument();
    });

    it('should prevent saving when duplicate column names exist', async () => {
      const duplicateColumns: Column[] = [
        { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col1', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];

      const { setColumns } = renderModal({ columns: duplicateColumns });

      await waitFor(() => {
        expect(screen.getByText('Column name "col1" must be unique')).toBeInTheDocument();
      });

      const doneButton = screen.getByRole('button', { name: 'Done' });
      expect(doneButton).toBeDisabled();

      const user = userEvent.setup();
      await user.click(doneButton);

      expect(setColumns).not.toHaveBeenCalled();
    });

    it('should prevent saving when empty column names exist', async () => {
      const columnsWithEmpty: Column[] = [
        { title: '', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];

      const { setColumns } = renderModal({ columns: columnsWithEmpty });

      await waitFor(() => {
        expect(screen.getByText('1 column(s) have empty names')).toBeInTheDocument();
      });

      const doneButton = screen.getByRole('button', { name: 'Done' });
      expect(doneButton).toBeDisabled();

      const user = userEvent.setup();
      await user.click(doneButton);

      expect(setColumns).not.toHaveBeenCalled();
    });

    it('should allow saving when duplicate names are fixed', async () => {
      const duplicateColumns: Column[] = [
        { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col1', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];

      const { setColumns } = renderModal({ columns: duplicateColumns });
      const user = userEvent.setup();

      // Initially should show error and disable button
      await waitFor(() => {
        expect(screen.getByText('Column name "col1" must be unique')).toBeInTheDocument();
      });
      expect(screen.getByRole('button', { name: 'Done' })).toBeDisabled();

      // Fix the duplicate by changing one name
      const nameInputs = screen.getAllByDisplayValue('col1');
      await user.clear(nameInputs[1]);
      await user.type(nameInputs[1], 'col2_fixed');

      // Error should disappear and button should be enabled
      await waitFor(() => {
        expect(screen.queryByText('Column name "col1" must be unique')).not.toBeInTheDocument();
      });

      const doneButton = screen.getByRole('button', { name: 'Done' });
      expect(doneButton).not.toBeDisabled();

      // Should now allow saving
      await user.click(doneButton);

      await waitFor(() => {
        expect(setColumns).toHaveBeenCalledWith([
          { ...duplicateColumns[0], title: 'col1', type: 'STRING', isPrimaryKey: false },
          { ...duplicateColumns[1], title: 'col2_fixed', type: 'INT', isPrimaryKey: false }
        ]);
      });
    });

    it('should show error status on inputs with validation errors', async () => {
      const duplicateColumns: Column[] = [
        { title: 'col1', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col1', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];

      renderModal({ columns: duplicateColumns });

      await waitFor(() => {
        const nameInputs = screen.getAllByDisplayValue('col1');
        // Both inputs should have error status since they're duplicates
        expect(nameInputs[0].closest('.ant-input')).toHaveClass('ant-input-status-error');
        expect(nameInputs[1].closest('.ant-input')).toHaveClass('ant-input-status-error');
      });
    });

    it('should allow saving when empty names are fixed', async () => {
      const columnsWithEmpty: Column[] = [
        { title: '', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col2', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];

      const { setColumns } = renderModal({ columns: columnsWithEmpty });
      const user = userEvent.setup();

      await waitFor(() => {
        expect(screen.getByText('1 column(s) have empty names')).toBeInTheDocument();
      });

      const emptyNameInput = screen.getAllByLabelText('Column title')[0];
      await user.type(emptyNameInput, 'fixed_name');

      await waitFor(() => {
        expect(screen.queryByText('1 column(s) have empty names')).not.toBeInTheDocument();
      });

      const doneButton = screen.getByRole('button', { name: 'Done' });
      expect(doneButton).not.toBeDisabled();

      await user.click(doneButton);

      await waitFor(() => {
        expect(setColumns).toHaveBeenCalledWith([
          {
            ...columnsWithEmpty[0],
            title: 'fixed_name',
            type: 'STRING',
            comment: 'comment1',
            isPrimaryKey: false
          },
          { ...columnsWithEmpty[1], type: 'INT', comment: 'comment2', isPrimaryKey: false }
        ]);
      });
    });

    it('should handle multiple validation errors simultaneously', async () => {
      const problematicColumns: Column[] = [
        { title: '', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'duplicate', dataIndex: 'col2', type: 'int', comment: 'comment2' },
        { title: 'duplicate', dataIndex: 'col3', type: 'string', comment: 'comment3' }
      ];

      const { setColumns } = renderModal({ columns: problematicColumns });

      await waitFor(() => {
        expect(
          screen.getByText('Column name "duplicate" must be unique. 1 column(s) have empty names')
        ).toBeInTheDocument();
      });

      const doneButton = screen.getByRole('button', { name: 'Done' });
      expect(doneButton).toBeDisabled();

      const user = userEvent.setup();
      await user.click(doneButton);

      expect(setColumns).not.toHaveBeenCalled();
    });

    it('should trim whitespace from column names during validation', async () => {
      const columnsWithWhitespace: Column[] = [
        { title: '  col1  ', dataIndex: 'col1', type: 'string', comment: 'comment1' },
        { title: 'col1', dataIndex: 'col2', type: 'int', comment: 'comment2' }
      ];

      renderModal({ columns: columnsWithWhitespace });

      await waitFor(() => {
        expect(screen.getByText('Column name "col1" must be unique')).toBeInTheDocument();
      });

      const doneButton = screen.getByRole('button', { name: 'Done' });
      expect(doneButton).toBeDisabled();
    });
  });

  describe('SQL types error handling', () => {
    it('should handle SQL type loading error and display error message', async () => {
      mockUseLoadData.mockReturnValue(MOCK_STATES.error);

      renderModal();

      await waitFor(() => {
        expect(
          screen.getByText(
            'Failed to fetch SQL types for engine hive, make sure the engine is properly configured in Hue.'
          )
        ).toBeInTheDocument();
      });

      expect(screen.queryByLabelText('Column type')).not.toBeInTheDocument();
    });

    it('should handle empty SQL types response and display error message', async () => {
      mockUseLoadData.mockReturnValue(MOCK_STATES.empty);

      renderModal();

      await waitFor(() => {
        expect(screen.getByText('No SQL types returned from server.')).toBeInTheDocument();
      });

      expect(screen.queryByLabelText('Column type')).not.toBeInTheDocument();
    });

    it('should handle SQL types loading state', () => {
      mockUseLoadData.mockReturnValue(MOCK_STATES.loading);

      renderModal();

      const typeSelects = getColumnTypeSelects();
      expect(typeSelects).toHaveLength(2);

      typeSelects.forEach(select => {
        expect(select).toHaveClass('ant-select-disabled');
        expect(select).toHaveClass('ant-select-loading');
      });

      expect(screen.getByText('Edit Columns')).toBeInTheDocument();
    });

    it('should handle invalid SQL type data format', async () => {
      mockUseLoadData.mockReturnValue(MOCK_STATES.invalidData);

      renderModal();

      await waitFor(() => {
        expect(screen.getByText('No SQL types returned from server.')).toBeInTheDocument();
      });

      expect(screen.queryByLabelText('Column type')).not.toBeInTheDocument();
    });
  });
});
