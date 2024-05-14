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
import './DropdownMenuItem.scss';

interface DropDownMenuItemProps {
  label: string;
  url: string;
  onFilepathChange: (path: string) => void;
}

const DropDownMenuItem = ({ label, url, onFilepathChange }: DropDownMenuItemProps): JSX.Element => {
  const handleFilepathChange = () => {
    onFilepathChange(url);
  };

  return (
    <div className="hue-path-browser__dropdown-item">
      <OverflowingItem label={label} onClick={handleFilepathChange}></OverflowingItem>
    </div>
  );
};

export default DropDownMenuItem;
