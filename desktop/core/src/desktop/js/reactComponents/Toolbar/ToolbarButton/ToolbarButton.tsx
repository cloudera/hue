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
import { Button } from 'antd';
import classNames from 'classnames';

import './ToolbarButton.scss';

enum IconPosition {
  left = 'left',
  right = 'right'
}

export interface ToolbarButtonProps {
  /** Make sure to use aria-label for icon only buttons */
  'aria-label'?: string;
  /** The contents of the button, normally the label but can be any JSX */
  children?: JSX.Element | string;
  /** String appended to the classname of the button wrapper */
  className?: string;
  /** Enable state of the button */
  disabled?: boolean;
  /** Setting the href will render the button using the anchor tag */
  href?: string;
  /** The icon to be displayed by the button, expects a react based icon like used in cuix */
  icon?: React.ReactNode;
  /** The position of the icon, defaults to left */
  iconPosition?: keyof typeof IconPosition;
  /** Callback for buttons, including anchor based ones using href */
  onClick?: () => void;
  /** Target when using href */
  target?: string;
  /** Test id */
  testId?: string;
  /** Optional title when using icon only or when additional context is needed */
  title?: string;
}

/**
 * ToolbarButton
 * A button for use in the Toolbar component.
 */
const ToolbarButton: FunctionComponent<ToolbarButtonProps> = ({
  'aria-label': ariaLabel,
  className,
  children,
  disabled,
  href,
  icon,
  iconPosition = IconPosition.left,
  onClick,
  target,
  testId = 'hue-toolbar-button',
  title
}) => {
  return (
    <React.StrictMode>
      <li data-testid={testId} className={classNames(className, 'hue-toolbar-button__wrapper')}>
        <Button
          aria-label={ariaLabel}
          className={'hue-toolbar-button'}
          data-testid={`${testId}-btn`}
          disabled={disabled}
          href={href}
          onClick={onClick}
          target={target}
          type="link"
          title={title}
        >
          <>
            {iconPosition === IconPosition.left && icon}
            {children}
            {iconPosition === IconPosition.right && icon}
          </>
        </Button>
      </li>
    </React.StrictMode>
  );
};

export default ToolbarButton;
