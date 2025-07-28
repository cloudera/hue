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
import { SQL_TYPE_MAPPING_API_URL } from '../../../admin/Components/utils';
import useLoadData from '../../../../utils/hooks/useLoadData/useLoadData';
import LoadingErrorWrapper from '../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './EditColumnsModal.scss';
import { ImporterTableData, BaseColumnProperties } from '../../types';

export interface Column extends BaseColumnProperties {
  title: string;
  dataIndex: string;
}

interface EditRow extends Required<BaseColumnProperties> {
  key: number;
  title: string;
  type: string;
  sample: string;
  comment: string;
}

interface EditColumnsModalProps {
  isOpen: boolean;
  closeModal: () => void;
  columns: Column[];
  setColumns: (cols: Column[]) => void;
  sample?: ImporterTableData;
}

const EditColumnsModal = ({
  isOpen,
  closeModal,
  columns,
  setColumns,
  sample
}: EditColumnsModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [editRows, setEditRows] = useState<EditRow[]>([]);

  const {
    data: sqlTypesData,
    loading: sqlTypesLoading,
    error: sqlTypesError
  } = useLoadData<string[]>(`${SQL_TYPE_MAPPING_API_URL}?sql_dialect=hive`);

  const sqlTypes = useMemo(() => {
    if (sqlTypesData && Array.isArray(sqlTypesData) && sqlTypesData.length > 0) {
      return sqlTypesData;
    }
    return [];
  }, [sqlTypesData]);

  const errors = [
    {
      enabled: !!sqlTypesError,
      message: t('Failed to fetch SQL types.')
    },
    {
      enabled: !sqlTypesLoading && sqlTypes.length === 0,
      message: t('No SQL types returned from server.')
    }
  ];

  useEffect(() => {
    setEditRows(
      columns.map((col, idx) => ({
        key: idx,
        title: col.title,
        type: (col.type || 'string').toUpperCase(),
        sample: sample && sample[col.dataIndex] !== undefined ? String(sample[col.dataIndex]) : '',
        comment: col.comment || ''
      }))
    );
  }, [columns, sample, isOpen]);

  const handleChange = (idx: number, field: keyof EditRow, value: string) => {
    setEditRows(rows => rows.map((row, i) => (i === idx ? { ...row, [field]: value } : row)));
  };

  const handleDone = async () => {
    const updatedColumns = editRows.map(row => ({
      ...columns[row.key],
      title: row.title,
      type: row.type,
      comment: row.comment
    }));
    setColumns(updatedColumns);
    closeModal();
  };

  const modalColumns = [
    {
      title: t('Name'),
      dataIndex: 'title',
      render: (text: string, _: EditRow, idx: number) => (
        <Input
          value={text}
          className="hue-importer-edit-columns-modal__input--name"
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            handleChange(idx, 'title', e.target.value)
          }
        />
      )
    },
    {
      title: t('Type'),
      dataIndex: 'type',
      render: (value: string, _: EditRow, idx: number) => (
        <Select
          value={value}
          onChange={(val: string) => handleChange(idx, 'type', val)}
          className="hue-importer-edit-columns-modal__select--type"
          getPopupContainer={triggerNode => triggerNode.parentNode}
          disabled={sqlTypesLoading || sqlTypes.length === 0}
          loading={sqlTypesLoading}
        >
          {sqlTypes.map(type => (
            <Select.Option key={type} value={type}>
              {type}
            </Select.Option>
          ))}
        </Select>
      )
    },
    {
      title: t('Sample'),
      dataIndex: 'sample',
      render: (text: string) => <span>{text}</span>
    },
    {
      title: t('Comment'),
      dataIndex: 'comment',
      render: (text: string, _: EditRow, idx: number) => (
        <textarea
          value={text}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
            handleChange(idx, 'comment', e.target.value)
          }
          rows={2}
        />
      )
    }
  ];

  return (
    <Modal
      open={isOpen}
      onCancel={closeModal}
      title={t('Edit Columns')}
      cancelText={t('Cancel')}
      okText={t('Done')}
      onOk={handleDone}
      className="cuix antd hue-importer-edit-columns-modal"
    >
      <LoadingErrorWrapper loading={sqlTypesLoading} errors={errors}>
        <Table columns={modalColumns} dataSource={editRows} pagination={false} />
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default EditColumnsModal;
