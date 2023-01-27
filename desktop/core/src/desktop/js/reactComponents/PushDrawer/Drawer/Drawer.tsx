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

import React, { FunctionComponent, useLayoutEffect, useState } from 'react';
import classNames from 'classnames';

import './Drawer.scss';

export interface DrawerProps {
  content: () => JSX.Element;
  direction: 'left' | 'right';
  header?: () => JSX.Element | null;
  isOpen: boolean;
  testId?: string;
  width: string;
}

const defaultProps = {
  testId: 'hue-push-drawer-drawer',
  header: () => null
};

const Drawer: FunctionComponent<DrawerProps> = ({
  content,
  direction,
  header,
  isOpen,
  testId,
  width
}) => {
  const [preventFocus, setPreventFocus] = useState<boolean>(!isOpen);

  useLayoutEffect(() => {
    if (isOpen && preventFocus) {
      setPreventFocus(false);
    }
  }, [isOpen]);

  const leftPosition =
    direction === 'left'
      ? isOpen
        ? '0px'
        : `-${width}`
      : `calc(100% - ${isOpen ? width : '0px'})`;

  return (
    <aside
      data-testid={testId}
      aria-hidden={!isOpen}
      style={{ width, left: leftPosition }}
      className={classNames('hue-push-drawer__drawer', `hue-push-drawer__drawer--${direction}`)}
      onTransitionEnd={() => {
        if (!isOpen) {
          setPreventFocus(true);
        }
      }}
    >
      <div
        data-testid={`${testId}-focus-preventer`}
        style={{
          // This prevents elements in the drawer to get focus when the
          // drawer is closed, while allowing for a smooth css transition.
          display: preventFocus ? 'none' : 'block'
        }}
      >
        {header?.()}
        {content()}
      </div>
    </aside>
  );
};

Drawer.defaultProps = defaultProps;
export default Drawer;
