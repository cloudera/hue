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
import DropdownButton from 'cuix/dist/components/DropdownButton';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import Button from 'cuix/dist/components/Button/Button';
import Tooltip from 'cuix/dist/components/Tooltip';
import { i18nReact } from '../../../utils/i18nReact';

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
  const { t } = i18nReact.useTranslation();

  // If no actions, return empty fragment
  if (!actions.length) {
    return <></>;
  }

  // If there's only one action, render it as a regular button
  if (actions.length === 1) {
    const action = actions[0];
    const ButtonComponent = action.variant === 'primary' ? PrimaryButton : Button;

    const buttonContent = (
      <ButtonComponent
        key={action.key}
        onClick={action.onClick}
        disabled={action.disabled || !!loading || !!isRefreshing}
        {...(action.variant === 'danger' && { danger: true })}
      >
        {action.icon && <span style={{ marginRight: action.label ? 8 : 0 }}>{action.icon}</span>}
        {action.label}
      </ButtonComponent>
    );

    return action.tooltip ? (
      <Tooltip title={action.tooltip}>{buttonContent}</Tooltip>
    ) : (
      buttonContent
    );
  }

  // For multiple actions, create menu items for all actions
  const menuItems = actions.map(action => ({
    key: action.key,
    label: action.label,
    icon: action.icon,
    disabled: action.disabled || !!loading || !!isRefreshing,
    onClick: action.onClick
  }));

  const menu = {
    items: menuItems
  };

  // Check if any action has a primary variant to determine button type
  const hasPrimaryAction = actions.some(action => action.variant === 'primary');

  // Render "Actions" dropdown button with all actions in the menu
  return (
    <DropdownButton
      label={t('Actions')}
      type={hasPrimaryAction ? 'primary' : 'default'}
      menu={menu}
      disabled={!!loading || !!isRefreshing}
    />
  );
};

export default Toolbar;
