// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React from 'react';
import { Input, Alert, Checkbox } from 'antd';
import Modal from 'cuix/dist/components/Modal';
import PathBrowser from '../../../../reactComponents/PathBrowser/PathBrowser';
import { i18nReact } from '../../../../utils/i18nReact';
import { post } from '../../../../api/utils';
import huePubSub from '../../../../utils/huePubSub';
import { notifyError } from '../../utils/notifier';
import { getConnectorIdOrType } from '../../utils/connector';
import type { Connector, Namespace, Compute } from '../../../../config/types';
import './ImportDataModal.scss';
import { useImportDataForm } from './useImportDataForm';

interface PartitionColumn {
  name: string;
  value: string;
}

interface ImportDataModalProps {
  open: boolean;
  onCancel: () => void;
  database: string;
  table: string;
  connector?: Connector | null;
  namespace?: Namespace | null;
  compute?: Compute | null;
  sourceType?: string;
  partitionColumns?: PartitionColumn[];
}

const ImportDataModal = ({
  open,
  onCancel,
  database,
  table,
  connector,
  namespace,
  compute,
  sourceType,
  partitionColumns = []
}: ImportDataModalProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();
  const { filePath, setFilePath, overwrite, setOverwrite, partitionValues, setPartitionValue } =
    useImportDataForm({ open, partitionColumns });
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string>('');

  const handleSubmit = async (): Promise<void> => {
    if (!filePath.trim()) {
      setError(t('Please specify a file path'));
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // Create form data similar to legacy implementation
      const formData = new URLSearchParams();
      formData.append('path', filePath.trim());
      formData.append('overwrite', overwrite ? 'on' : 'off');
      formData.append('is_embeddable', 'true');
      formData.append('source_type', sourceType || getConnectorIdOrType(connector) || 'hive');
      formData.append('start_time', Date.now().toString());

      // Add partition column values
      Object.entries(partitionValues).forEach(([key, value]) => {
        if (value.trim()) {
          formData.append(key, value.trim());
        }
      });

      if (namespace) {
        formData.append('namespace', JSON.stringify(namespace));
      }

      if (compute) {
        formData.append('cluster', JSON.stringify(compute));
      }

      const result = await post<{
        status: number;
        data?: string;
        history_uuid?: string;
        message?: string;
      }>(
        `/metastore/table/${encodeURIComponent(database)}/${encodeURIComponent(table)}/load`,
        formData,
        {
          silenceErrors: false,
          qsEncodeData: false
        }
      );

      if (result.status === 0) {
        // Success - publish notebook task submitted event
        if (result.history_uuid) {
          huePubSub.publish('notebook.task.submitted', result);
        }
        onCancel(); // Close modal
      } else if (result.status === 1) {
        // Form validation error
        setError(result.data || t('Failed to import data'));
      } else {
        // Other error
        setError(result.message || t('Failed to import data'));
      }
    } catch (err) {
      // debug: import data error
      notifyError(t('Failed to import data'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const isSubmitDisabled = !filePath.trim() || isSubmitting;

  return (
    <Modal
      open={open}
      title={t('Import Data')}
      okText={t('Submit')}
      cancelText={t('Cancel')}
      onCancel={onCancel}
      onOk={handleSubmit}
      okButtonProps={{
        disabled: isSubmitDisabled,
        loading: isSubmitting
      }}
      width={680}
    >
      <div className="import-data-modal__section">
        <label className="import-data-modal__label">{t('Path')} *</label>
        <PathBrowser
          filePath={filePath}
          onFilepathChange={setFilePath}
          testId="import-data-path-browser"
        />
        <div className="import-data-modal__note">
          {t('Path to the file or directory to import')}
        </div>
      </div>

      {partitionColumns.length > 0 && (
        <div className="import-data-modal__section">
          <div className="import-data-modal__label">{t('Partition Values')}</div>
          {partitionColumns.map(col => (
            <div key={col.name} className="import-data-modal__partition-field">
              <label className="import-data-modal__partition-label">{col.name}</label>
              <Input
                value={partitionValues[col.name] || ''}
                onChange={e => setPartitionValue(col.name, e.target.value)}
                placeholder={t('Enter value for {{columnName}}', { columnName: col.name })}
                maxLength={512}
              />
            </div>
          ))}
        </div>
      )}

      <div className="import-data-modal__section">
        <Checkbox checked={overwrite} onChange={e => setOverwrite(e.target.checked)}>
          {t('Overwrite existing data')}
        </Checkbox>
      </div>

      <Alert
        message={t(
          "Note that loading data will move data from its location into the table's storage location."
        )}
        type="warning"
        showIcon
        className="import-data-modal__alert"
      />

      {error && (
        <Alert message={error} type="error" showIcon className="import-data-modal__alert" />
      )}
    </Modal>
  );
};

export default ImportDataModal;
