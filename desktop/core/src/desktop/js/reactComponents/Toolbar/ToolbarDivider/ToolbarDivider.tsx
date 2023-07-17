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

import { Divider } from 'antd';
import React, { FunctionComponent } from 'react';

import './ToolbarDivider.scss';

export interface ToolbarDividerProps {
  testId?: string;
}

const ToolbarDivider: FunctionComponent<ToolbarDividerProps> = ({
  testId = 'hue-toolbar-divider'
}: ToolbarDividerProps) => (
  <li className="hue-toolbar-divider" data-testid={testId}>
    <Divider type="vertical" />
  </li>
);

export default ToolbarDivider;
