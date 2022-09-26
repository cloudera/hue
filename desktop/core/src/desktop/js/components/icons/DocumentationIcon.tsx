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

const DocumentationIcon = (props: SVGProps<SVGSVGElement>): JSX.Element => (
  <svg viewBox="0 0 24 24" fill="none" width="1em" height="1em" {...props}>
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M14.413 2L20 7.585V22H4V2h10.413zm-2.414 2H6v16h12V9.999L12 10l-.001-6zM16 16v2H8v-2h8zm0-4v2H8v-2h8zm-6-4v2H8V8h2zm3.999-3.586L14 7.999h3.585l-3.586-3.585z"
      fill="currentColor"
    />
  </svg>
);

export default DocumentationIcon;
