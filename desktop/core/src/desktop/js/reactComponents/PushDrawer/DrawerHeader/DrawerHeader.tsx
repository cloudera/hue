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

import React, { FunctionComponent } from 'react';

import { i18nReact } from '../../../utils/i18nReact';
import CloseIcon from '../../../components/icons/CloseIcon';

import './DrawerHeader.scss';

export interface DrawerHeaderProps {
  closeBtnAriaLabel?: string;
  onClose: () => void;
  testId?: string;
  title?: string;
}

const defaultProps = {
  testId: 'hue-push-drawer-header'
};

const DrawerHeader: FunctionComponent<DrawerHeaderProps> = ({ onClose, testId, ...i18n }) => {
  const { t } = i18nReact.useTranslation();
  const { closeBtnAriaLabel = t('Close'), title } = i18n;

  return (
    <div className="hue-push-drawer-header" data-testid={`${testId}`}>
      <h3 className="hue-h3 hue-push-drawer-header__title" data-testid={`${testId}-title`}>
        {title}
      </h3>
      <button
        data-testid={`${testId}-close-btn`}
        aria-label={closeBtnAriaLabel}
        className="hue-push-drawer-header__close-btn"
        onClick={onClose}
      >
        <CloseIcon data-testid={`${testId}-close-icon`} />
      </button>
    </div>
  );
};

DrawerHeader.defaultProps = defaultProps;
export default DrawerHeader;
