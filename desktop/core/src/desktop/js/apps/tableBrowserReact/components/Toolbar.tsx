// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information.
// Apache License 2.0 applies.

import React, { useState } from 'react';
import { Space } from 'antd';
import Modal from 'cuix/dist/components/Modal';
import Tooltip from 'cuix/dist/components/Tooltip';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import Button from 'cuix/dist/components/Button/Button';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';

import { i18nReact } from '../../../utils/i18nReact';
import huePubSub from '../../../utils/huePubSub';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';

export interface ToolbarAction {
  key: string;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'default' | 'danger';
  tooltip?: string;
  icon?: React.ReactNode;
}

export interface ToolbarProps {
  // Legacy props for backward compatibility
  sourceType?: string;
  database?: string;
  table?: string;
  onRefresh?: () => void;
  onDrop?: (skipTrash?: boolean) => Promise<void> | void;
  onLoadData?: () => Promise<void> | void;
  showQuery?: boolean;
  showLoadData?: boolean;
  showDrop?: boolean;
  showRefresh?: boolean;

  // New props for listing pages
  actions?: ToolbarAction[];
  selectedItems?: string[];
  loading?: boolean;
  isRefreshing?: boolean;
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
  showRefresh = true,
  actions,
  loading,
  isRefreshing
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
  const [skipTrash, setSkipTrash] = useState(false);

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
        onCancel={() => {
          setConfirmOpen(false);
          setSkipTrash(false);
        }}
        onOk={async () => {
          try {
            if (onDrop) {
              await onDrop(skipTrash);
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
          setSkipTrash(false);
        }}
      >
        <div style={{ marginBottom: 16 }}>
          {t('Do you really want to drop the table')}{' '}
          <strong>{database && table ? `${database}.${table}` : ''}</strong>?
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={skipTrash}
            onChange={e => setSkipTrash(e.target.checked)}
          />
          {t('Skip the trash')}
        </label>
      </Modal>

      <Space>
        {/* New action-based rendering */}
        {actions ? (
          actions.map(action => {
            // Special handling for refresh actions - always use BorderlessButton with RefreshIcon
            if (action.key === 'refresh') {
              const buttonContent = (
                <BorderlessButton
                  key={action.key}
                  onClick={action.onClick}
                  disabled={action.disabled || !!loading || !!isRefreshing}
                  title={action.tooltip || action.label}
                  icon={<RefreshIcon />}
                >
                  {action.label}
                </BorderlessButton>
              );

              return action.tooltip ? (
                <Tooltip key={action.key} title={action.tooltip}>
                  {buttonContent}
                </Tooltip>
              ) : (
                buttonContent
              );
            }

            // Standard handling for other actions
            const ButtonComponent = action.variant === 'primary' ? PrimaryButton : Button;
            const buttonProps = {
              key: action.key,
              onClick: action.onClick,
              disabled: action.disabled || !!loading || !!isRefreshing,
              ...(action.variant === 'danger' && { danger: true })
            };

            const buttonContent = (
              <ButtonComponent {...buttonProps}>
                {action.icon && (
                  <span style={{ marginRight: action.label ? 8 : 0 }}>{action.icon}</span>
                )}
                {action.label}
              </ButtonComponent>
            );

            return action.tooltip ? (
              <Tooltip key={action.key} title={action.tooltip}>
                {buttonContent}
              </Tooltip>
            ) : (
              buttonContent
            );
          })
        ) : (
          /* Legacy rendering for backward compatibility */
          <>
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
            {showRefresh && (
              <BorderlessButton onClick={onRefresh} title={t('Refresh')} icon={<RefreshIcon />}>
                {t('Refresh')}
              </BorderlessButton>
            )}
          </>
        )}
      </Space>
    </>
  );
};

export default Toolbar;
