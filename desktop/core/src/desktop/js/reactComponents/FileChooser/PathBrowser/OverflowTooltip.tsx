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

import React, { ReactElement, ReactNode } from 'react';
import { Tooltip } from 'antd';

interface OverflowTooltipProps {
  title: string;
  isOverflowing: boolean;
  toolTipTriggers: string | string[];
  children: ReactNode | ReactElement;
}

const OverflowTooltip: React.FC<OverflowTooltipProps> = ({
  title,
  isOverflowing,
  toolTipTriggers,
  children
}) => {
  return isOverflowing ? (
    <Tooltip title={title} trigger={toolTipTriggers}>
      {children}
    </Tooltip>
  ) : (
    <>{children}</>
  );
};

export default OverflowTooltip;
