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

interface OverflowingItemProps {
  label: string;
  onClick: () => void;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-path-browser__overflowing'
};

const OverflowingItem: React.FC<OverflowingItemProps> = ({ label, onClick, testId }) => {
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
        onClick={onClick}
        data-testid={`${testId}-label`}
      >
        {label}
      </Button>
    </OverflowTooltip>
  );
};

OverflowingItem.defaultProps = defaultProps;
export default OverflowingItem;
