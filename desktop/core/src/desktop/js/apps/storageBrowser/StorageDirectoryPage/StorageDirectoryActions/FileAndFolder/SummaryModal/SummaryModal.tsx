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
import Modal from 'cuix/dist/components/Modal';

import { i18nReact } from '../../../../../../utils/i18nReact';
import formatBytes from '../../../../../../utils/formatBytes';
import useLoadData from '../../../../../../utils/hooks/useLoadData/useLoadData';
import { CONTENT_SUMMARY_API_URL } from '../../../../api';
import { ContentSummary, StorageDirectoryTableData } from '../../../../types';
import LoadingErrorWrapper from '../../../../../../reactComponents/LoadingErrorWrapper/LoadingErrorWrapper';

import './SummaryModal.scss';

interface SummaryModalProps {
  path: StorageDirectoryTableData['path'];
  isOpen?: boolean;
  onClose: () => void;
}

const SummaryModal = ({ isOpen = true, onClose, path }: SummaryModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { data, loading, error, reloadData } = useLoadData<ContentSummary>(
    CONTENT_SUMMARY_API_URL,
    {
      params: { path: path },
      skip: path === '' || path === undefined
    }
  );

  const summary = [
    {
      key: 'diskspaceConsumed',
      label: t('Diskspace Consumed'),
      value: formatBytes(data?.spaceConsumed)
    },
    { key: 'bytesUsed', label: t('Bytes Used'), value: formatBytes(data?.length) },
    {
      key: 'namespaceQuota',
      label: t('Namespace Quota'),
      value: formatBytes(data?.quota)
    },
    {
      key: 'diskspaceQuota',
      label: t('Diskspace Quota'),
      value: formatBytes(data?.spaceQuota)
    },
    {
      key: 'replicationFactor',
      label: t('Replication Factor'),
      value: data?.replication
    },
    { key: 'blank', label: '', value: '' },
    {
      key: 'numberOfDirectories',
      label: t('Number of Directories'),
      value: data?.directoryCount
    },
    { key: 'numberOfFiles', label: t('Number of Files'), value: data?.fileCount }
  ];

  const errors = [
    {
      enabled: !!error,
      message: error,
      actionText: t('Retry'),
      onClick: reloadData
    }
  ];

  const shortendPath =
    path.split('/').length > 4 ? '...' + path.split('/').slice(-4).join('/') : path;

  return (
    <Modal
      open={isOpen}
      title={t('Summary for ') + shortendPath}
      className="cuix antd"
      onCancel={onClose}
      footer={false}
    >
      <LoadingErrorWrapper loading={loading} errors={errors} hideOnError>
        <div className="hue-summary-modal__grid">
          {summary?.map(item => (
            <div key={item.key} className="hue-summary-modal__grid__summary-item">
              <div className="hue-summary-modal__grid__summary-item__label">{item.label}</div>
              <div className="hue-summary-modal__grid__summary-item__value">{item.value}</div>
            </div>
          ))}
        </div>
      </LoadingErrorWrapper>
    </Modal>
  );
};

export default SummaryModal;
