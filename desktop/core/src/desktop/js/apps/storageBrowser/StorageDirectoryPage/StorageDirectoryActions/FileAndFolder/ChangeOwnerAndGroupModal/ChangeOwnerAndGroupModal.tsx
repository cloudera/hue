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

import React, { useEffect, useMemo, useState } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { i18nReact } from '../../../../../../utils/i18nReact';
import useSaveData from '../../../../../../utils/hooks/useSaveData/useSaveData';
import { Checkbox, Input, Select } from 'antd';
import { HDFSFileSystemConfig, StorageDirectoryTableData } from '../../../../types';
import { BULK_CHANGE_OWNER_API_URL } from '../../../../api';
import LoadingErrorWrapper from '../../../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './ChangeOwnerAndGroupModal.scss';

interface ChangeOwnerAndGroupModalProps {
  superUser?: HDFSFileSystemConfig['superuser'];
  superGroup?: HDFSFileSystemConfig['supergroup'];
  users?: HDFSFileSystemConfig['users'];
  groups?: HDFSFileSystemConfig['groups'];
  isOpen?: boolean;
  files: StorageDirectoryTableData[];
  onSuccess: () => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

const OTHERS_KEY = 'others';
const getDropdownOptions = (
  entity: HDFSFileSystemConfig['users'] | HDFSFileSystemConfig['groups']
) => {
  return [...entity, OTHERS_KEY].map(user => ({
    value: user,
    label: user
  }));
};

const ChangeOwnerAndGroupModal = ({
  superUser,
  superGroup,
  users = [],
  groups = [],
  isOpen = true,
  files,
  onSuccess,
  onError,
  onClose
}: ChangeOwnerAndGroupModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const [selectedUser, setSelectedUser] = useState<string>(files[0].user);
  const [selectedGroup, setSelectedGroup] = useState<string>(files[0].group);
  const [userOther, setUserOther] = useState<string>();
  const [groupOther, setGroupOther] = useState<string>();
  const [isRecursive, setIsRecursive] = useState<boolean>(false);

  const { save, loading, error } = useSaveData(BULK_CHANGE_OWNER_API_URL, {
    skip: !files.length,
    onSuccess,
    onError
  });

  const handleChangeOwner = () => {
    const formData = new FormData();
    if (selectedUser === OTHERS_KEY && userOther) {
      formData.append('user', userOther);
    } else {
      formData.append('user', selectedUser);
    }
    if (selectedGroup === OTHERS_KEY && groupOther) {
      formData.append('group', groupOther);
    } else {
      formData.append('group', selectedGroup);
    }
    if (isRecursive) {
      formData.append('recursive', String(isRecursive));
    }
    files.forEach(file => {
      formData.append('path', file.path);
    });

    save(formData);
  };

  const usersOptions = getDropdownOptions(users);
  const groupOptions = getDropdownOptions(groups);

  useEffect(() => {
    const isOtherUserSelected = !users.includes(files[0].user);
    if (isOtherUserSelected) {
      setSelectedUser(OTHERS_KEY);
      setUserOther(files[0].user);
    }

    const isOtherGroupSelected = !groups.includes(files[0].group);
    if (isOtherGroupSelected) {
      setSelectedGroup(OTHERS_KEY);
      setGroupOther(files[0].group);
    }
  }, []);

  const isSubmitEnabled = useMemo(() => {
    return Boolean(
      selectedUser &&
        selectedGroup &&
        !(selectedUser === OTHERS_KEY && !userOther) &&
        !(selectedGroup === OTHERS_KEY && !groupOther)
    );
  }, [selectedUser, selectedGroup, userOther, groupOther]);

  const errors = [{ enabled: !!error, message: error }];

  return (
    <Modal
      open={isOpen}
      title={t('Change Owner / Group')}
      className="cuix antd"
      okText={t('Submit')}
      onOk={handleChangeOwner}
      okButtonProps={{ disabled: !isSubmitEnabled, loading }}
      cancelText={t('Cancel')}
      onCancel={onClose}
      cancelButtonProps={{ disabled: loading }}
      closable={!loading}
    >
      <LoadingErrorWrapper errors={errors}>
        <div className="hue-change-owner-group">
          <span className="hue-change-owner-group__header-note">
            {t(
              'Note: Only the Hadoop superuser, "{{superuser}}" or the HDFS supergroup, "{{supergroup}}" on this file system, may change the owner of a file.',
              {
                superuser: superUser,
                supergroup: superGroup
              }
            )}
          </span>

          <div className="hue-change-owner-group__form">
            <div className="hue-change-owner-group__entity">
              <div className="hue-change-owner-group__label">{t('User')}</div>
              <div className="hue-change-owner-group__dropdown">
                <Select
                  options={usersOptions}
                  onChange={setSelectedUser}
                  value={selectedUser}
                  disabled={loading}
                  getPopupContainer={triggerNode => triggerNode.parentElement}
                />
                {selectedUser === OTHERS_KEY && (
                  <Input
                    placeholder={t('Enter user')}
                    value={userOther}
                    onChange={e => setUserOther(e.target.value)}
                    disabled={loading}
                    required
                  />
                )}
              </div>
            </div>

            <div className="hue-change-owner-group__entity">
              <div className="hue-change-owner-group__label">{t('Group')}</div>
              <div className="hue-change-owner-group__dropdown">
                <Select
                  options={groupOptions}
                  onChange={setSelectedGroup}
                  value={selectedGroup}
                  disabled={loading}
                  getPopupContainer={triggerNode => triggerNode.parentElement}
                />
                {selectedGroup === OTHERS_KEY && (
                  <Input
                    placeholder={t('Enter group')}
                    value={groupOther}
                    onChange={e => setGroupOther(e.target.value)}
                    disabled={loading}
                    required
                  />
                )}
              </div>
            </div>

            <div className="hue-change-owner-group__checkbox">
              <span className="hue-change-owner-group__label">{t('Recursive')}</span>
              <Checkbox
                checked={isRecursive}
                onChange={() => setIsRecursive(prev => !prev)}
                disabled={loading}
                name="recursive"
              />
            </div>
          </div>
        </div>
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default ChangeOwnerAndGroupModal;
