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


/**
 * Toolbar - TODO: add this
 */

export interface ToolbarProps {
  /** One or more ToolbarButtons and ToolbarSeparators. For multiple elements use a wrapping fragment. */
  content: () => JSX.Element;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-toolbar'
};

const Toolbar: FunctionComponent<ToolbarProps> = ({ content, testId }) => {
  return (
    <React.StrictMode>
      <menu className="hue-toolbar" data-testid={testId}>
        {content()}
      </menu>
    </React.StrictMode>
  );
};

Toolbar.defaultProps = defaultProps;
export default Toolbar;
