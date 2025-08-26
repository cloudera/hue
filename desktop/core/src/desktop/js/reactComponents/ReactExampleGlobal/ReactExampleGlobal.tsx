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

'use strict';

import React, { useState } from 'react';

import { i18nReact } from '../../utils/i18nReact';
import hueAnalytics from '../../utils/hueAnalytics';

import './ReactExampleGlobal.scss';

export interface ReactExampleGlobalProps {
  onClick?(e: React.MouseEvent): void;
  version?: string;
  myObj?: { id: string };
  className?: string;
  children?: React.ReactNode | React.ReactNode[];
}

const ReactExampleGlobal = ({
  onClick,
  children,
  version = '1',
  myObj,
  className
}: ReactExampleGlobalProps): JSX.Element => {
  const [isClicked, setIsClicked] = useState(false);

  // We use the translation hook with the built in suspence,
  // meaning that this component won't render until the language file
  // have been loaded.
  const { t } = i18nReact.useTranslation();

  return (
    <button
      className={`react-example-global ${className || ''}`}
      disabled={isClicked}
      onClick={e => {
        onClick && onClick(e);
        setIsClicked(true);
        console.info(`ReactExampleGlobal clicked  ${version} ${myObj?.id}`);
        hueAnalytics.log('test-area', 'button click', true);
      }}
    >
      ReactExampleGlobal - {children ?? t('Yes')}
    </button>
  );
};

export default ReactExampleGlobal;
