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

import React, { useState, useEffect, ChangeEvent, useMemo } from 'react';
import { i18nReact } from '../../../../utils/i18nReact';
import Modal from 'cuix/dist/components/Modal';
import Table from 'cuix/dist/components/Table';
import Input from 'cuix/dist/components/Input';
import Select from 'cuix/dist/components/Select';
import { Alert, Checkbox } from 'antd';
import { SQL_TYPE_MAPPING_API_URL } from '../../../admin/Components/utils';
import useLoadData from '../../../../utils/hooks/useLoadData/useLoadData';
import LoadingErrorWrapper from '../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './EditColumnsModal.scss';
import { ImporterTableData, BaseColumnProperties } from '../../types';

export interface Column extends BaseColumnProperties {
  title: string;
  dataIndex: string;
}

interface EditableRow extends Required<BaseColumnProperties> {
  key: number;
  title: string;
  type: string;
  sample: string;
  comment: string;
  isPrimaryKey: boolean;
}

interface EditColumnsModalProps {
  isOpen: boolean;
  closeModal: () => void;
  columns: Column[];
  setColumns: (cols: Column[]) => void;
  sample?: ImporterTableData;
  sqlDialect?: string;
  fileFormat?: {
    type?: string;
    fieldSeparator?: string;
    hasHeader?: boolean;
  };
}

const EditColumnsModal = ({
  isOpen,
  closeModal,
  columns,
  setColumns,
  sample,
  sqlDialect = 'hive',
  fileFormat
}: EditColumnsModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [editableRows, setEditableRows] = useState<EditableRow[]>([]);

  const {
    data: sqlTypesData,
    loading: sqlTypesLoading,
    error: sqlTypesError
  } = useLoadData<string[]>(`${SQL_TYPE_MAPPING_API_URL}?sql_dialect=${sqlDialect}`);

  const sqlTypes = useMemo(() => {
    if (sqlTypesData && Array.isArray(sqlTypesData) && sqlTypesData.length > 0) {
      return sqlTypesData;
    }
    return [];
  }, [sqlTypesData]);

  const validateColumnNames = useMemo(() => {
    const errors = new Set<number>();
    const titleCounts = new Map<string, number[]>();

    editableRows.forEach((row, index) => {
      const title = row.title.trim();

      if (!title) {
        errors.add(index);
      }

      if (!titleCounts.has(title)) {
        titleCounts.set(title, []);
      }
      titleCounts.get(title)!.push(index);
    });

    titleCounts.forEach(indices => {
      if (indices.length > 1) {
        indices.forEach(index => errors.add(index));
      }
    });

    return { errors, duplicates: titleCounts };
  }, [editableRows]);

  const sampleDataAnalysis = useMemo(() => {
    const missingSampleCount = editableRows.filter(row => !row.sample.trim()).length;

    if (missingSampleCount === 0) {
      return { recommendations: [] };
    }

    const isCompletelyMissing = missingSampleCount === editableRows.length;
    const fileType = fileFormat?.type;

    const getFileSpecificGuidance = () => {
      if (fileType === 'csv') {
        return t('Check CSV settings: field separator, quote character, or "Has Header" option.');
      }
      if (fileType === 'excel') {
        return t('Try different Excel sheet or verify sheet contains data.');
      }
      if (fileType === 'json') {
        return t('Verify JSON structure and data format.');
      }
      return t('Check file format settings and data structure.');
    };

    const message = isCompletelyMissing
      ? `${t('No sample data detected.')} ${getFileSpecificGuidance()} ${t('Import may fail.')}`
      : `${t('{{count}} columns missing data.', { count: missingSampleCount })} ${t('Verify column types before importing.')}`;

    return {
      recommendations: [message],
      hasNoSampleData: isCompletelyMissing,
      hasPartialSampleData: !isCompletelyMissing
    };
  }, [editableRows, fileFormat, t]);

  const hasValidationErrors = validateColumnNames.errors.size > 0;

  const getValidationErrorMessages = (): string[] => {
    const messages: string[] = [];
    const duplicateNames = new Set<string>();

    validateColumnNames.duplicates.forEach((indices, title) => {
      if (indices.length > 1 && title.trim()) {
        duplicateNames.add(title.trim());
      }
    });

    if (duplicateNames.size > 0) {
      duplicateNames.forEach(name => {
        messages.push(t('Column name "{{name}}" must be unique', { name }));
      });
    }

    const emptyCount = Array.from(validateColumnNames.errors).filter(
      index => !editableRows[index]?.title.trim()
    ).length;

    if (emptyCount > 0) {
      messages.push(t('{{count}} column(s) have empty names', { count: emptyCount }));
    }

    return messages;
  };

  const errors = [
    {
      enabled: !!sqlTypesError,
      message: t(
        'Failed to fetch SQL types for engine {{engine}}, make sure the engine is properly configured in Hue.',
        { engine: sqlDialect }
      )
    },
    {
      enabled: !sqlTypesLoading && sqlTypes.length === 0,
      message: t('No SQL types returned from server.')
    }
  ];

  useEffect(() => {
    setEditableRows(
      columns.map((col, idx) => ({
        key: idx,
        title: col.title,
        type: (col.type || 'string').toUpperCase(),
        sample: sample && sample[col.dataIndex] !== undefined ? String(sample[col.dataIndex]) : '',
        comment: col.comment || '',
        isPrimaryKey: col.isPrimaryKey || false
      }))
    );
  }, [columns, sample]);

  const handleChange = (rowIndex: number, field: keyof EditableRow, value: string | boolean) => {
    setEditableRows(rows =>
      rows.map((row, i) => (i === rowIndex ? { ...row, [field]: value } : row))
    );
  };

  const handleDone = async () => {
    if (hasValidationErrors) {
      return;
    }

    const updatedColumns = editableRows.map(row => ({
      ...columns[row.key],
      title: row.title.trim(),
      type: row.type,
      comment: row.comment,
      isPrimaryKey: row.isPrimaryKey
    }));
    setColumns(updatedColumns);
    closeModal();
  };

  const modalColumns = [
    {
      title: t('P Key'),
      dataIndex: 'isPrimaryKey',
      className: 'hue-importer-edit-columns-modal__primary-key',
      render: (isPrimaryKey: boolean, _: EditableRow, rowIndex: number) => (
        <Checkbox
          checked={isPrimaryKey}
          onChange={e => handleChange(rowIndex, 'isPrimaryKey', e.target.checked)}
          aria-label={t('Set as primary key')}
        />
      )
    },
    {
      title: t('Title'),
      dataIndex: 'title',
      render: (text: string, _: EditableRow, rowIndex: number) => (
        <Input
          value={text}
          className="hue-importer-edit-columns-modal__input-title"
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            handleChange(rowIndex, 'title', e.target.value)
          }
          aria-label={t('Column title')}
          status={validateColumnNames.errors.has(rowIndex) ? 'error' : undefined}
        />
      )
    },
    {
      title: t('Type'),
      dataIndex: 'type',
      render: (value: string, _: EditableRow, rowIndex: number) => (
        <Select
          value={value}
          onChange={(val: string) => handleChange(rowIndex, 'type', val)}
          className="hue-importer-edit-columns-modal__type-select"
          getPopupContainer={triggerNode => triggerNode.parentNode}
          disabled={sqlTypesLoading || sqlTypes.length === 0}
          loading={sqlTypesLoading}
          options={sqlTypes.map(type => ({ label: type, value: type }))}
          aria-label={t('Column type')}
        />
      )
    },
    {
      title: t('Sample'),
      dataIndex: 'sample',
      render: (text: string) => {
        if (text) {
          return <span>{text}</span>;
        }

        const allEmpty = editableRows.every(row => !row.sample.trim());
        const warningText = allEmpty ? t('Check file format') : t('Empty column');

        return (
          <span className="hue-importer-edit-columns-modal__no-sample" title={warningText}>
            {t('No data')}
          </span>
        );
      }
    },
    {
      title: t('Comment'),
      dataIndex: 'comment',
      render: (text: string, _: EditableRow, rowIndex: number) => (
        <textarea
          value={text}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
            handleChange(rowIndex, 'comment', e.target.value)
          }
          rows={2}
          aria-label={t('Column comment')}
        />
      )
    }
  ];

  const validationErrorMessages = getValidationErrorMessages();

  return (
    <Modal
      open={isOpen}
      onCancel={closeModal}
      title={t('Edit Columns')}
      cancelText={t('Cancel')}
      okText={t('Done')}
      onOk={handleDone}
      okButtonProps={{ disabled: hasValidationErrors }}
      className="hue-importer-edit-columns-modal"
    >
      <LoadingErrorWrapper loading={sqlTypesLoading} errors={errors} hideOnError={true}>
        {validationErrorMessages.length > 0 && (
          <Alert
            message={validationErrorMessages.join('. ')}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        {sampleDataAnalysis.recommendations.length > 0 && (
          <Alert
            message={sampleDataAnalysis.recommendations.join(' ')}
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        <Table columns={modalColumns} dataSource={editableRows} pagination={false} />
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default EditColumnsModal;
