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

const S3Icon = (props: SVGProps<SVGSVGElement>): JSX.Element => (
  <svg viewBox="0 0 24 24" fill="none" width="1em" height="1em" {...props}>
    <path d="M12.1 17.302l7.634 1.848V4.817L12.1 6.665v10.637z" fill="#8C3123" />
    <path
      d="M19.734 4.817l1.467.733v12.87l-1.467.734V4.817zM15.43 7.373l-3.33-.824V1l3.33 1.665v4.708zM12.1 23l3.33-1.664v-4.708l-3.33.823V23zM15.43 14.357l-3.33.424V9.23l3.33.418v4.708zM12.1 17.302L4.466 19.15V4.817L12.1 6.665v10.637z"
      fill="#E05243"
    />
    <path
      d="M4.466 4.817L3 5.55v12.87l1.466.734V4.817zM8.772 7.373l3.328-.824V1L8.772 2.665v4.708zM12.1 23l-3.329-1.664v-4.708l3.33.823V23zM8.772 14.357l3.328.424V9.23l-3.328.418v4.708z"
      fill="#8C3123"
    />
    <path d="M15.43 7.373l-3.33.606-3.328-.606 3.328-.824 3.33.824z" fill="#5E1F18" />
    <path d="M15.43 16.628l-3.33-.61-3.328.61 3.328.829 3.33-.83z" fill="#F2B0A9" />
  </svg>
);

export default S3Icon;
