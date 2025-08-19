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
import { Button } from 'antd';
import { MinusCircleOutlined } from '@ant-design/icons';
import { ColumnProps } from 'cuix/dist/components/Table';
import { i18nReact } from '../../../utils/i18nReact';
import FormInput, { FieldType } from '../../../reactComponents/FormInput/FormInput';
import { Partition } from '../types';
import PaginatedTable from '../../../reactComponents/PaginatedTable/PaginatedTable';

import './PartitionsTab.scss';
import { LinkButton } from 'cuix/dist/components/Button';

interface PartitionsTabProps {
  partitions: Partition[];
  onPartitionsChange: (partitions: Partition[]) => void;
}

// TODO: check if this comes from API call based on dialect
const PARTITION_TYPE_OPTIONS = [
  { value: 'string', label: 'String' },
  { value: 'int', label: 'Integer' },
  { value: 'bigint', label: 'Big Integer' },
  { value: 'float', label: 'Float' },
  { value: 'double', label: 'Double' },
  { value: 'boolean', label: 'Boolean' },
  { value: 'timestamp', label: 'Timestamp' },
  { value: 'date', label: 'Date' }
];

const PartitionsTab = ({ partitions, onPartitionsChange }: PartitionsTabProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const handlePartitionChange = (partitionId: string, fieldName: string, value: string) => {
    const updatedPartitions = partitions.map(partition =>
      partition.id === partitionId ? { ...partition, [fieldName]: value } : partition
    );

    onPartitionsChange(updatedPartitions);
  };

  const handleAddPartition = () => {
    const newPartition: Partition = {
      id: `partition_${Date.now()}`,
      name: '',
      type: 'string',
      value: ''
    };

    onPartitionsChange([...partitions, newPartition]);
  };

  const handleRemovePartition = (partitionId: string) => {
    const updatedPartitions = partitions.filter(partition => partition.id !== partitionId);

    onPartitionsChange(updatedPartitions);
  };

  const getTableColumns = (): ColumnProps<Partition>[] => [
    {
      title: t('Name'),
      dataIndex: 'name',
      key: 'name',
      render: (_, partition: Partition) => (
        <FormInput
          field={{
            name: 'name',
            type: FieldType.INPUT,
            placeholder: t('Partition name')
          }}
          value={partition.name}
          onChange={(fieldName, value) =>
            handlePartitionChange(partition.id, fieldName, value as string)
          }
        />
      )
    },
    {
      title: t('Type'),
      dataIndex: 'type',
      key: 'type',
      render: (_, partition: Partition) => (
        <FormInput
          field={{
            name: 'type',
            type: FieldType.SELECT,
            placeholder: t('Choose type'),
            options: PARTITION_TYPE_OPTIONS
          }}
          value={partition.type}
          onChange={(fieldName, value) =>
            handlePartitionChange(partition.id, fieldName, value as string)
          }
        />
      )
    },
    {
      title: t('Value'),
      dataIndex: 'value',
      key: 'value',
      render: (_, partition: Partition) => (
        <FormInput
          field={{
            name: 'value',
            type: FieldType.INPUT,
            placeholder: t('Partition value')
          }}
          value={partition.value}
          onChange={(fieldName, value) =>
            handlePartitionChange(partition.id, fieldName, value as string)
          }
        />
      )
    },
    {
      title: '',
      key: 'actions',
      width: 50,
      render: (_, partition: Partition) => (
        <Button
          type="text"
          icon={<MinusCircleOutlined />}
          onClick={() => handleRemovePartition(partition.id)}
          className="hue-partitions-tab__delete-button"
        />
      )
    }
  ];

  return (
    <div className="hue-partitions-tab">
      <LinkButton className="hue-partitions-tab__add-button" onClick={handleAddPartition}>
        {`+ ${t('Add partitions')}`}
      </LinkButton>

      {partitions.length > 0 && (
        <PaginatedTable
          data={partitions}
          columns={getTableColumns()}
          rowKey={(record: Partition) => record.id}
        />
      )}
    </div>
  );
};

export default PartitionsTab;
