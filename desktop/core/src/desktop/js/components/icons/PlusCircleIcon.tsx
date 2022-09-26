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

const PlusCircleIcon = (props: SVGProps<SVGSVGElement>): JSX.Element => (
  <svg viewBox="0 0 24 24" fill="none" width="1em" height="1em" {...props}>
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M17 11h-4V7h-2v4H7v2h4v4h2v-4h4v-2zm-5-7c-4.411 0-8 3.589-8 8s3.589 8 8 8 8-3.589 8-8-3.589-8-8-8zm0 18C6.486 22 2 17.514 2 12S6.486 2 12 2s10 4.486 10 10-4.486 10-10 10z"
      fill="currentColor"
    />
  </svg>
);

export default PlusCircleIcon;
