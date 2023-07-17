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

import React from 'react';

import './CommonHeader.scss';

interface CommonHeaderProps {
  title: string;
  icon: JSX.Element;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-header'
};

const CommonHeader: React.FC<CommonHeaderProps> = ({ title, icon, testId }) => {
  return (
    <div className="hue-common-header" data-testid={testId}>
      <div className="hue-header-icon" data-testid={`${testId}-icon`}>
        {icon}
      </div>
      <div className="hue-header-title" data-testid={`${testId}-title`}>
        {title}
      </div>
      {/* TODO: Add actions dropdown*/}
    </div>
  );
};

CommonHeader.defaultProps = defaultProps;

export default CommonHeader;
