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
import { Spin } from 'antd';

import huePubSub from '../../../../utils/huePubSub';
import { i18nReact } from '../../../../utils/i18nReact';
import formatBytes from '../../../../utils/formatBytes';
import useLoadData from '../../../../utils/hooks/useLoadData';
import { CONTENT_SUMMARY_API_URL } from '../../../../reactComponents/FileChooser/api';
import { ContentSummary } from '../../../../reactComponents/FileChooser/types';

import './SummaryModal.scss';

interface SummaryModalProps {
  path: string;
  showModal: boolean;
  onClose: () => void;
}

const SummaryModal = ({ showModal, onClose, path }: SummaryModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const { data: responseSummary, loading } = useLoadData<ContentSummary>(CONTENT_SUMMARY_API_URL, {
    params: { path },
    onError: error => {
      huePubSub.publish('hue.error', error);
    },
    skip: path === '' || path === undefined || !showModal
  });

  const summary = [
    {
      key: 'diskspaceConsumed',
      label: t('Diskspace Consumed'),
      value: formatBytes(responseSummary?.spaceConsumed)
    },
    { key: 'bytesUsed', label: t('Bytes Used'), value: formatBytes(responseSummary?.length) },
    {
      key: 'namespaceQuota',
      label: t('Namespace Quota'),
      value: formatBytes(responseSummary?.quota)
    },
    {
      key: 'diskspaceQuota',
      label: t('Diskspace Quota'),
      value: formatBytes(responseSummary?.spaceQuota)
    },
    {
      key: 'replicationFactor',
      label: t('Replication Factor'),
      value: responseSummary?.replication
    },
    { key: 'blank', label: '', value: '' },
    {
      key: 'numberOfDirectories',
      label: t('Number of Directories'),
      value: responseSummary?.directoryCount
    },
    { key: 'numberOfFiles', label: t('Number of Files'), value: responseSummary?.fileCount }
  ];

  //TODO:Handle long modal title
  return (
    <Modal
      className="hue-summary-modal cuix antd"
      okText={t('Close')}
      onOk={onClose}
      open={showModal}
      title={t('Summary for ') + path}
      cancellable={false}
      onCancel={onClose}
    >
      <Spin spinning={loading}>
        <div className="hue-summary-modal__grid">
          {summary?.map(item => (
            <div key={item.key} className="hue-summary-modal__grid__summary-item">
              <div className="hue-summary-modal__grid__summary-item__label">{item.label}</div>
              <div className="hue-summary-modal__grid__summary-item__value">{item.value}</div>
            </div>
          ))}
        </div>
      </Spin>
    </Modal>
  );
};

export default SummaryModal;
