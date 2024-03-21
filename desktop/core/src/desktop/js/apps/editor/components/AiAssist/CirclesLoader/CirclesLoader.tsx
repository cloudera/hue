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

import './CirclesLoader.scss';

function CirclesLoader({
  repeatCount = 'indefinite',
  duration = '1.5s'
}: {
  repeatCount?: number | string;
  duration?: string;
}): JSX.Element {
  const cy = '12';
  const renderAnimation = begin => (
    <animate
      attributeName="r"
      begin={begin}
      calcMode="spline"
      dur={duration}
      keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8"
      repeatCount={repeatCount}
      values="0;2;0;0"
    />
  );

  return (
    <svg
      className="hue-ai-assist-bar__circles-loader"
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
    >
      <circle className="hue-ai-assist-bar__circles-loader-circle" cx="18" cy={cy} r="0">
        {renderAnimation('.67')}
      </circle>
      <circle className="hue-ai-assist-bar__circles-loader-circle" cx="12" cy={cy} r="0">
        {renderAnimation('.33')}
      </circle>
      <circle className="hue-ai-assist-bar__circles-loader-circle" cx="6" cy={cy} r="0">
        {renderAnimation('0')}
      </circle>
    </svg>
  );
}

export default CirclesLoader;
