/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import React from 'react';
import classNames from 'classnames';

import './AnimatedCloseButton.scss';

type Size = 'small' | 'large';
type Direction = 'left' | 'right';

type Props = {
  title: string;
  className?: string;
  onClick: () => void;
  size?: Size;
  direction?: Direction;
};

function AnimatedCloseButton({
  title,
  className,
  onClick,
  size = 'large',
  direction = 'left'
}: Props): JSX.Element {
  return (
    <div
      title={title}
      className={classNames(
        'hue-animated-close-button',
        className,
        `hue-animated-close-button--${size}`,
        `hue-animated-close-button--${direction}`
      )}
      onClick={onClick}
    >
      <span></span>
      <span></span>
      <span></span>
    </div>
  );
}

export default AnimatedCloseButton;
