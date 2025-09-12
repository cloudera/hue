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
import { Space } from 'antd';
import Tooltip from 'cuix/dist/components/Tooltip';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import Button from 'cuix/dist/components/Button/Button';
import RefreshIcon from '@cloudera/cuix-core/icons/react/RefreshIcon';
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
  actions: ToolbarAction[];
  selectedItems?: string[];
  loading?: boolean;
  isRefreshing?: boolean;
}

const Toolbar = ({ actions, loading, isRefreshing }: ToolbarProps): JSX.Element => {
  return (
    <Space>
      {actions.map(action => {
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
      })}
    </Space>
  );
};

export default Toolbar;
