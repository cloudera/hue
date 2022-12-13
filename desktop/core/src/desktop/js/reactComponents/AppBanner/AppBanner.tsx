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

import React, { useEffect, useState } from 'react';
import sanitizeHtml, { IOptions } from 'sanitize-html';

import './AppBanner.scss';
import { BANNERS_API } from '../../api/urls';
import { get } from '../../api/utils';
import deXSS from '../../utils/html/deXSS';
import noop from '../../utils/timing/noop';

interface ApiBanners {
  system?: string;
  configured?: string;
}

const allowedCssColorRegex = [
  /^#(0x)?[0-9a-f]+$/i,
  /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/
];
const allowedCssSizeRegex = [/^[\d.]+(?:px|pt|em|%|rem|vw)$/i];

// Based on defaults from https://github.com/apostrophecms/sanitize-html with support for a select set of styles that
// would make sense to use in a banner.
const sanitizeOptions: IOptions = {
  allowedAttributes: {
    '*': ['style'],
    ...sanitizeHtml.defaults.allowedAttributes
  },
  allowedStyles: {
    '*': {
      background: allowedCssColorRegex,
      'background-color': allowedCssColorRegex,
      color: allowedCssColorRegex,
      direction: [/^ltr|rtl$/i],
      'font-size': allowedCssSizeRegex,
      height: allowedCssSizeRegex,
      padding: allowedCssSizeRegex,
      'padding-bottom': allowedCssSizeRegex,
      'padding-left': allowedCssSizeRegex,
      'padding-right': allowedCssSizeRegex,
      'padding-top': allowedCssSizeRegex,
      'text-align': [/^left|right|center$/i],
      width: allowedCssSizeRegex
    }
  }
};

export const AppBanner = (): JSX.Element => {
  const [banners, setBanners] = useState<ApiBanners>();

  useEffect(() => {
    if (!banners) {
      get<ApiBanners>(BANNERS_API).then(setBanners).catch(noop);
    }
  });

  return (
    banners &&
    (banners.system ? (
      <div
        className={'app-banner app-banner--system'}
        dangerouslySetInnerHTML={{ __html: banners.system }}
      />
    ) : (
      <div
        className={'app-banner'}
        dangerouslySetInnerHTML={{ __html: deXSS(banners.configured, sanitizeOptions) }}
      />
    ))
  );
};

export default AppBanner;
