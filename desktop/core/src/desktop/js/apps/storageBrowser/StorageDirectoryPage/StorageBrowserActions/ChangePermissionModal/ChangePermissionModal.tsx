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
import Modal from 'cuix/dist/components/Modal';
import { i18nReact } from '../../../../../utils/i18nReact';
import useSaveData from '../../../../../utils/hooks/useSaveData/useSaveData';
import { Checkbox, Table } from 'antd';
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import { BULK_CHANGE_PERMISSION_API_URL } from '../../../../../reactComponents/FileChooser/api';
import { getInitialPermissions, Permission } from './ChangePermissionModal.util';

import './ChangePermissionModal.scss';

interface ChangePermissionModalProps {
  isOpen?: boolean;
  files: StorageDirectoryTableData[];
  setLoading: (value: boolean) => void;
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const ChangePermissionModal = ({
  isOpen = true,
  files,
  setLoading,
  onSuccess,
  onError,
  onClose
}: ChangePermissionModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const initialPermissions = getInitialPermissions(files);
  const [permissions, setPermissions] = useState<Permission[]>(initialPermissions);

  const { save, loading } = useSaveData(BULK_CHANGE_PERMISSION_API_URL, {
    postOptions: {
      qsEncodeData: false
    },
    skip: !files.length,
    onSuccess,
    onError
  });

  const handleChangeOwner = () => {
    setLoading(true);

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
      return <Checkbox checked={value} onChange={() => handleCheckboxChange(record.key, key)} />;
    }
  };

  const columns = [
    {
      title: '',
      dataIndex: 'key',
      key: 'key'
    },
    {
      title: 'User',
      dataIndex: 'user',
      key: 'user',
      render: renderTableCheckbox('user')
    },
    {
      title: 'Group',
      dataIndex: 'group',
      key: 'group',
      render: renderTableCheckbox('group')
    },
    {
      title: 'Other',
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

  return (
    <Modal
      cancelText={t('Cancel')}
      className="cuix antd"
      okText={t('Submit')}
      onCancel={onClose}
      onOk={handleChangeOwner}
      open={isOpen}
      title={t('Change Permissions')}
      okButtonProps={{ disabled: loading }}
      cancelButtonProps={{ disabled: loading }}
    >
      <Table
        dataSource={permissions}
        columns={columns}
        pagination={false}
        className="hue-change-permission__table"
      />
    </Modal>
  );
};

export default ChangePermissionModal;
