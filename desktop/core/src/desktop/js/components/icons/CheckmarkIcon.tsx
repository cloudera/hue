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

const CheckmarkIcon = (props: SVGProps<SVGSVGElement>): JSX.Element => (
  <svg viewBox="0 0 24 24" fill="none" width="1em" height="1em" {...props}>
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M9.675 15.899l-4.262-4.262L4 13.052l5.656 5.657 11.318-11.31L19.574 6l-9.899 9.899z"
      fill="currentColor"
    />
  </svg>
);

export default CheckmarkIcon;
