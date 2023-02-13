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

import React, { FunctionComponent } from 'react';
import { Button, Icon } from 'antd';
import { ButtonType } from 'antd/lib/button';
import classNames from 'classnames';

import './ToolbarButton.scss';

type ToolbarButtonType = 'primary' | 'default' | 'iconOnly' | 'link' | 'borderless';

// trying to align with the API of the cuix button since
// we are planning on using the cuix library in hue.
export interface ToolbarButtonProps {
  'aria-label'?: string;
  children?: JSX.Element | string;
  className?: string;
  href?: string;
  htmlType?: 'button' | 'reset' | 'submit';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onClick?: () => void;
  testId?: string;
  type: ToolbarButtonType;
}

const defaultProps = {
  testId: 'hue-toolbar-button',
  iconPosition: 'left'
};

const convertToAntdButtonType = (type: ToolbarButtonType): ButtonType => {
  switch (type) {
    case 'iconOnly':
      return 'text';
    case 'borderless':
      return 'text';
    default:
      return type;
  }
};

/**
 * ToolbarButton - TODO: add this
 */
const ToolbarButton: FunctionComponent<ToolbarButtonProps> = ({
  className,
  children,
  icon,
  iconPosition,
  testId,
  type
}) => {
  console.info('iconPosition', iconPosition);
  return (
    <React.StrictMode>
      <li data-testid={testId} className={className}>
        <Button
          className={'hue-toolbar-button'}
          data-testd={testId}
          type={convertToAntdButtonType(type)}
        >
          <>
            {iconPosition === 'left' && icon}
            {children ?? children}
            {iconPosition === 'right' && icon}
          </>
        </Button>
      </li>
    </React.StrictMode>
  );
};

ToolbarButton.defaultProps = defaultProps;
export default ToolbarButton;
