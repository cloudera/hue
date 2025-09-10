// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information.
// Apache License 2.0 applies.

import React, { useState } from 'react';
import { Space } from 'antd';
import Modal from 'cuix/dist/components/Modal';
import Tooltip from 'cuix/dist/components/Tooltip';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import Button from 'cuix/dist/components/Button/Button';
import { i18nReact } from '../../../utils/i18nReact';
import huePubSub from '../../../utils/huePubSub';

export interface ToolbarProps {
  sourceType?: string;
  database?: string;
  table?: string;
  onRefresh?: () => void;
  onDrop?: () => Promise<void> | void;
  onLoadData?: () => Promise<void> | void;
  showQuery?: boolean;
  showLoadData?: boolean;
  showDrop?: boolean;
  showRefresh?: boolean;
}

const Toolbar = ({
  sourceType,
  database,
  table,
  onRefresh,
  onDrop,
  onLoadData,
  showQuery = true,
  showLoadData = false,
  showDrop = false,
  showRefresh = true
}: ToolbarProps): JSX.Element => {
  const { t } = i18nReact.useTranslation();

  const openQuery = (): void => {
    const type = sourceType || 'hive';
    const query = database && table ? `SELECT * FROM ${database}.${table} LIMIT 100;` : '';
    huePubSub.publish('open.editor.new.prefilled.query', {
      type,
      query
    });
  };

  const [confirmOpen, setConfirmOpen] = useState(false);
  const dropTable = (): void => {
    if (!database || !table) {
      return;
    }
    setConfirmOpen(true);
  };

  return (
    <>
      <Modal
        open={confirmOpen}
        title={t('Drop table')}
        okText={t('Drop')}
        okButtonProps={{ danger: true }}
        cancelText={t('Cancel')}
        onCancel={() => setConfirmOpen(false)}
        onOk={async () => {
          try {
            if (onDrop) {
              await onDrop();
            }
            if (onRefresh) {
              onRefresh();
            }
          } catch (e) {
            if (onRefresh) {
              onRefresh();
            }
          }
          setConfirmOpen(false);
        }}
      >
        <div>{database && table ? `${database}.${table}` : ''}</div>
      </Modal>

      <Space>
        {showQuery && <PrimaryButton onClick={openQuery}>{t('Query')}</PrimaryButton>}
        {showLoadData && (
          <Tooltip title={t('Load data into table')}>
            <Button onClick={() => onLoadData?.()} disabled={!database || !table}>
              {t('Load Data')}
            </Button>
          </Tooltip>
        )}
        {showDrop && (
          <Tooltip title={t('Drop table')}>
            <Button onClick={dropTable} disabled={!database || !table}>
              {t('Drop')}
            </Button>
          </Tooltip>
        )}
        {showRefresh && <Button onClick={onRefresh}>{t('Refresh')}</Button>}
      </Space>
    </>
  );
};

export default Toolbar;
