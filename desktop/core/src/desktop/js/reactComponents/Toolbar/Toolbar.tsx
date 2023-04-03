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
import classNames from 'classnames';

import ToolbarButtonExport from './ToolbarButton/ToolbarButton';
import ToolbarDividerExport from './ToolbarDivider/ToolbarDivider';

import './Toolbar.scss';
export const ToolbarButton = ToolbarButtonExport;
export const ToolbarDivider = ToolbarDividerExport;

enum Size {
  small = 'small',
  medium = 'medium',
  large = 'large'
}

/**
 * Toolbar
 * A toolbar component based on the menu tag that uses the content view prop to display
 * ToolbarButtons, ToolbarDividers or any custom JSX elements that wrap its content in
 * an li element.
 */
export interface ToolbarProps {
  className?: string;
  /** One or more ToolbarButtons and ToolbarSeparators. For multiple elements use a wrapping fragment. */
  content: () => JSX.Element;
  /** Defaults to medium with a height of 40px with ToolbarButton icons & font-size matching cuix button medium size */
  size?: keyof typeof Size;
  testId?: string;
}

const Toolbar: FunctionComponent<ToolbarProps> = ({
  className,
  content,
  size = Size.medium,
  testId = 'hue-toolbar'
}) => (
  <React.StrictMode>
    <menu
      className={classNames('hue-toolbar', `hue-toolbar--${size}`, className)}
      data-testid={testId}
    >
      {content()}
    </menu>
  </React.StrictMode>
);

export default Toolbar;
