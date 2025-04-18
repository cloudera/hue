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

import React, { useState } from 'react';
import { Checkbox } from 'antd';
import Modal from 'cuix/dist/components/Modal';
import { i18nReact } from '../../../../../../utils/i18nReact';
import useSaveData from '../../../../../../utils/hooks/useSaveData/useSaveData';
import PaginatedTable, {
  ColumnProps
} from '../../../../../../reactComponents/PaginatedTable/PaginatedTable';
import { StorageDirectoryTableData } from '../../../../types';
import { BULK_CHANGE_PERMISSION_API_URL } from '../../../../api';
import { getInitialPermissions, Permission } from './ChangePermissionModal.util';
import LoadingErrorWrapper from '../../../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './ChangePermissionModal.scss';

interface ChangePermissionModalProps {
  isOpen?: boolean;
  files: StorageDirectoryTableData[];
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const ChangePermissionModal = ({
  isOpen = true,
  files,
  onSuccess,
  onError,
  onClose
}: ChangePermissionModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const initialPermissions = getInitialPermissions(files);
  const [permissions, setPermissions] = useState<Permission[]>(initialPermissions);

  const { save, loading, error } = useSaveData(BULK_CHANGE_PERMISSION_API_URL, {
    skip: !files.length,
    onSuccess,
    onError
  });

  const handleChangeOwner = () => {
    const formData = new FormData();
    const perm = permissions.reduce((acc, { key, user, group, other, common }) => {
      if (user) {
        acc[`user_${key}`] = user;
      }
      if (group) {
        acc[`group_${key}`] = group;
      }
      if (other) {
        acc[`other_${key}`] = other;
      }
      if (common) {
        acc[key] = common;
      }
      return acc;
    }, {});

    formData.append('permission', JSON.stringify(perm));

    files.forEach(file => {
      formData.append('path', file.path);
    });

    save(formData);
  };

  const handleCheckboxChange = (key: string, column: keyof Permission) => {
    setPermissions(prev =>
      prev.map(item => (item.key === key ? { ...item, [column]: !item[column] } : item))
    );
  };

  const renderTableCheckbox = (key: keyof Permission) => (value: boolean, record: Permission) => {
    if (value !== undefined) {
      return (
        <Checkbox
          checked={value}
          onChange={() => handleCheckboxChange(record.key, key)}
          disabled={loading}
        />
      );
    }
  };

  const columns: ColumnProps<Permission>[] = [
    {
      title: '',
      dataIndex: 'key',
      key: 'key'
    },
    {
      title: t('User'),
      dataIndex: 'user',
      key: 'user',
      render: renderTableCheckbox('user')
    },
    {
      title: t('Group'),
      dataIndex: 'group',
      key: 'group',
      render: renderTableCheckbox('group')
    },
    {
      title: t('Other'),
      dataIndex: 'other',
      key: 'other',
      render: renderTableCheckbox('other')
    },
    {
      title: '',
      dataIndex: 'common',
      key: 'common',
      render: renderTableCheckbox('common')
    }
  ];

  const errors = [{ enabled: !!error, message: error }];

  return (
    <Modal
      cancelText={t('Cancel')}
      className="cuix antd"
      okText={t('Submit')}
      onCancel={onClose}
      onOk={handleChangeOwner}
      open={isOpen}
      title={t('Change Permissions')}
      okButtonProps={{
        loading,
        disabled: JSON.stringify(initialPermissions) === JSON.stringify(permissions)
      }}
      cancelButtonProps={{ disabled: loading }}
      closable={!loading}
    >
      <LoadingErrorWrapper errors={errors}>
        <PaginatedTable<Permission> data={permissions} columns={columns} rowKey="key" />
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default ChangePermissionModal;
