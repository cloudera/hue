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

interface Column {
  title: string;
  dataIndex: string;
  type?: string;
  comment?: string;
}

interface EditRow {
  key: number;
  name: string;
  type: string;
  sample: string;
  comment: string;
}

interface EditColumnsModalProps {
  isOpen: boolean;
  closeModal: () => void;
  columns: Column[];
  setColumns: (cols: Column[]) => void;
  sample?: Record<string, any>[];
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

  useEffect(() => {
    setEditRows(
      columns.map((col, idx) => ({
        key: idx,
        name: col.title,
        type: col.type || 'string',
        sample: sample && sample.length > 0 ? (sample[0][col.dataIndex] ?? '') : '',
        comment: col.comment || ''
      }))
    );
  }, [columns, sample, isOpen]);

  const handleChange = (idx: number, field: keyof EditRow, value: string) => {
    setEditRows(rows => rows.map((row, i) => (i === idx ? { ...row, [field]: value } : row)));
  };

  const handleDone = () => {
    setColumns(
      editRows.map(row => ({
        ...columns[row.key],
        title: row.name,
        type: row.type,
        comment: row.comment
      }))
    );
    closeModal();
  };

  const modalColumns = useMemo(
    () => [
      {
        title: t('Column Name'),
        dataIndex: 'name',
        render: (text: string, _: EditRow, idx: number) => (
          <Input
            value={text}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              handleChange(idx, 'name', e.target.value)
            }
            placeholder={t('Column Name')}
          />
        )
      },
      {
        title: t('Column Type'),
        dataIndex: 'type',
        render: (value: string, _: EditRow, idx: number) => (
          <Select
            value={value}
            onChange={(val: string) => handleChange(idx, 'type', val)}
            getPopupContainer={triggerNode => triggerNode.parentNode}
            style={{ border: '1px solid #838b92', borderRadius: '3px', width: '150px' }}
          >
            <Select.Option value="string">{t('String')}</Select.Option>
            <Select.Option value="int">{t('Integer')}</Select.Option>
            <Select.Option value="float">{t('Float')}</Select.Option>
            <Select.Option value="bool">{t('Boolean')}</Select.Option>
          </Select>
        )
      },
      {
        title: t('Sample Value'),
        dataIndex: 'sample',
        render: (text: string, _: EditRow, idx: number) => (
          <Input
            value={text}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              handleChange(idx, 'sample', e.target.value)
            }
            style={{ border: 'none' }}
          />
        )
      },
      {
        title: t('Comment'),
        dataIndex: 'comment',
        render: (text: string, _: EditRow, idx: number) => (
          <Input
            value={text}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              handleChange(idx, 'comment', e.target.value)
            }
          />
        )
      }
    ],
    [t]
  );

  return (
    <Modal
      open={isOpen}
      onCancel={closeModal}
      title={t('Edit Columns')}
      cancelText={t('cancel')}
      okText={t('Done')}
      onOk={handleDone}
      width={800}
    >
      <Table columns={modalColumns} dataSource={editRows} pagination={false} />
    </Modal>
  );
};

export default EditColumnsModal;
