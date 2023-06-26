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

import React, { useEffect, useRef, useState } from 'react';
import { Button } from 'antd';

import OverflowTooltip from './OverflowTooltip';
import './OverflowingItem.scss';

type OverflowingComponentType = 'breadcrumb' | 'menu';
interface OverflowingItemProps {
  label: string;
  url: string;
  handleFilePathChange: (path: string) => void;
  componentType: OverflowingComponentType;
}

//TODO: change to add classnames to components instead of inline styles
const customStyles: {
  [key in OverflowingComponentType]: React.CSSProperties;
} = {
  breadcrumb: {
    minWidth: '5ch'
  },
  menu: {
    width: '100%',
    textAlign: 'left'
  }
};

const OverflowingItem: React.FC<OverflowingItemProps> = ({
  label,
  url,
  handleFilePathChange,
  componentType
}) => {
  const textElementRef = useRef<HTMLDivElement>(null);
  const [isOverflown, setIsOverflown] = useState(false);

  const compareSize = () => {
    const element = textElementRef.current;

    const compare = element
      ? element.offsetWidth < element.scrollWidth || element.offsetHeight < element.scrollHeight
      : false;
    setIsOverflown(compare);
  };

  useEffect(() => {
    compareSize();
    window.addEventListener('resize', compareSize);
    return () => {
      window.removeEventListener('resize', compareSize);
    };
  }, []);

  return (
    <OverflowTooltip isOverflowing={isOverflown} title={label} toolTipTriggers={['hover', 'focus']}>
      <Button
        ref={textElementRef}
        className="hue-path-browser__overflowing-label"
        onClick={() => {
          handleFilePathChange(url);
        }}
        style={customStyles[componentType]}
      >
        {label}
      </Button>
    </OverflowTooltip>
  );
};

export default OverflowingItem;
