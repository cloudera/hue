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

const GSIcon = (props: SVGProps<SVGSVGElement>): JSX.Element => (
  <svg viewBox="0 0 32 32" fill="none" fill-rule="evenodd" width="1em" height="1em" {...props}>
    <path fill="#5C85DE" d="M0 4h3v11H0zm29 0h3v11h-3z"></path>
    <path fill="#3367D6" d="M29 15V4h1.815z"></path>
    <path fill="#85A4E6" d="M3 4v11h26V4H3zm12 7H6V8h9v3zm9 .5a2 2 0 110-4 2 2 0 010 4z"></path>
    <path fill="#5C85DE" d="M0 17h3v11H0zm29 0h3v11h-3z"></path>
    <path fill="#3367D6" d="M29 28V17h1.815z"></path>
    <path fill="#85A4E6" d="M3 17v11h26V17H3zm12 7H6v-3h9v3zm9 .5a2 2 0 110-4 2 2 0 010 4z"></path>
  </svg>
);

export default GSIcon;
