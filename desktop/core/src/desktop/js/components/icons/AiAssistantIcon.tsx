// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { SVGProps } from 'react';

const AiAssistantIcon = (props: SVGProps<SVGSVGElement>): JSX.Element => (
  <svg
    className="ai-assist-icon"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <path
      className="ai-assist-icon__star-1"
      d="M1.99927 7.2074L5.83848 5.82412L7.20674 1.99993L8.58055 5.82412L12.4142 7.2074L8.58055 8.58472L7.20674 12.4149L5.81069 8.58472L1.99927 7.2074Z"
      fill="currentColor"
    />
    <path
      className="ai-assist-icon__star-2"
      d="M8.86548 13.0592L13.7071 11.3147L15.4326 6.49204L17.1652 11.3147L21.9998 13.0592L17.1652 14.7961L15.4326 19.6264L13.6721 14.7961L8.86548 13.0592Z"
      fill="currentColor"
    />
    <path
      className="ai-assist-icon__star-3"
      d="M3.5 18.1742L6.32065 17.1579L7.3259 14.3483L8.33523 17.1579L11.1518 18.1742L8.33523 19.1861L7.3259 22.0001L6.30023 19.1861L3.5 18.1742Z"
      fill="currentColor"
    />
  </svg>
);

export default AiAssistantIcon;
