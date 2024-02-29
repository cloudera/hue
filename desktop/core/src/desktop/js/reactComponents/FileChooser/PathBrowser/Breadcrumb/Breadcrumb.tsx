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

import OverflowingItem from '../OverflowingItem';
import './Breadcrumb.scss';

interface BreadcrumbProps {
  label: string;
  url: string;
  onFilepathChange: (path: string) => void;
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({ label, url, onFilepathChange }) => {
  const handleFilepathChange = () => {
    onFilepathChange(url);
  };

  const minWidth = '' + (label.length < 10 ? label.length : 10) + 'ch';

  return (
    <div
      className="hue-path-browser__breadcrumb"
      style={{ '--minWidth': `${minWidth}` } as React.CSSProperties}
    >
      <OverflowingItem onClick={handleFilepathChange} label={label} />
    </div>
  );
};

export default Breadcrumb;
