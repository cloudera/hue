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
import React, { useEffect, useState } from 'react';
import Modal from 'cuix/dist/components/Modal';
import { Row, Col, Spin } from 'antd';

import huePubSub from '../../../utils/huePubSub';
import { i18nReact } from '../../../utils/i18nReact';
import formatBytes from '../../../utils/formatBytes';
import { fetchContentSummary } from '../../../reactComponents/FileChooser/api';
import './SummaryModal.scss';
import { ContentSummary } from '../../../reactComponents/FileChooser/types';

interface SummaryModalProps {
  path: string;
  showModal: boolean;
  onClose: () => void;
}

const SummaryModal = ({ showModal, onClose, path }: SummaryModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [summary, setSummary] = useState([]);

  const getSummary = () => {
    const cols = summary.map((item, index) => (
      <Col key={'summaryItem' + index} span={12}>
        <Row key={'summaryItem' + index + 'key'}>{item[0]}</Row>
        <Row key={'summaryItem' + index + 'value'}>{item[1]}</Row>
      </Col>
    ));

    const rows = [];
    for (let i = 0; i < cols.length - 1; i = i + 2) {
      rows.push(
        <Row key={'summaryRow' + i} className="hue-summary-modal__row">
          {cols[i]}
          {cols[i + 1]}
        </Row>
      );
    }
    return rows;
  };

  const updateSummaryData = (responseSummary: ContentSummary) => {
    const summaryData = [
      ['DISKSPACE CONSUMED', formatBytes(responseSummary.summary.spaceConsumed)],
      ['BYTES USED', formatBytes(responseSummary.summary.length)],
      ['NAMESPACE QUOTA', formatBytes(responseSummary.summary.quota)],
      ['DISKSPACE QUOTA', formatBytes(responseSummary.summary.spaceQuota)],
      ['REPLICATION FACTOR', responseSummary.summary.replication],
      [,],
      ['NUMBER OF DIRECTORIES', responseSummary.summary.directoryCount],
      ['NUMBER OF FILES', responseSummary.summary.fileCount]
    ];
    setSummary(summaryData);
  };

  useEffect(() => {
    if (path === '') {
      return;
    }
    setLoadingSummary(true);
    fetchContentSummary(path)
      .then(responseSummary => {
        updateSummaryData(responseSummary);
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        onClose();
      })
      .finally(() => {
        setLoadingSummary(false);
      });
  }, [path]);

  //TODO:Handle long modal title
  return (
    <Modal
      className="hue-summary-modal"
      okText={t('Close')}
      onOk={onClose}
      open={showModal}
      title={t('Summary for ') + path}
      cancellable={false}
      onCancel={onClose}
    >
      <Spin spinning={loadingSummary}>{summary && getSummary()}</Spin>
    </Modal>
  );
};

export default SummaryModal;
