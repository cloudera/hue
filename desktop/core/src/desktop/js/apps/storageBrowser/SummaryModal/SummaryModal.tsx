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
import { content_summary } from '../../../reactComponents/FileChooser/api';
import './SummaryModal.scss';

interface SummaryModalProps {
  path: string;
  showModal: boolean;
  onClose: () => void;
}

const SummaryModal: React.FC<SummaryModalProps> = ({ showModal, onClose, path }): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [summary, setSummary] = useState([]);

  const formatBytes = (bytes, decimals) => {
    if (bytes == -1) {
      return 'Not available';
    }
    if (bytes == 0) {
      return '0 Byte';
    }
    const k = 1024;
    const dm = decimals + 1 || 3;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toPrecision(dm) + ' ' + sizes[i];
  };

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

  useEffect(() => {
    if (path === '') {
      return;
    }
    setLoadingSummary(true);
    content_summary(path)
      .then(responseSummary => {
        const summaryData = [
          ['DISKSPACE CONSUMED', formatBytes(responseSummary.summary.spaceConsumed, 4)],
          ['BYTES USED', formatBytes(responseSummary.summary.length, 4)],
          ['NAMESPACE QUOTA', formatBytes(responseSummary.summary.quota, 4)],
          ['DISKSPACE QUOTA', formatBytes(responseSummary.summary.spaceQuota, 4)],
          ['REPLICATION FACTOR', responseSummary.summary.replication],
          [,],
          ['NUMBER OF DIRECTORIES', responseSummary.summary.directoryCount],
          ['NUMBER OF FILES', responseSummary.summary.fileCount]
        ];
        setSummary(summaryData);
      })
      .catch(error => {
        huePubSub.publish('hue.error', error);
        onClose();
      })
      .finally(() => {
        setLoadingSummary(false);
      });
  }, [path]);

  return (
    <Modal
      className="hue-summary-modal"
      okText={t('Close')}
      onOk={() => {
        onClose();
      }}
      open={showModal}
      title={t('Summary for ') + path}
      cancellable={false}
      onCancel={() => {
        onClose();
      }}
    >
      <Spin spinning={loadingSummary}>{summary ? getSummary() : <div />}</Spin>
    </Modal>
  );
};

export default SummaryModal;
