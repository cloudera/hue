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

import i18next, { InitOptions } from 'i18next';
import HttpApi from 'i18next-http-backend';
import {
  initReactI18next,
  useTranslation,
  UseTranslationOptions,
  UseTranslationResponse
} from 'react-i18next';
import { hueWindow } from 'types/types';

// eslint-disable-next-line @typescript-eslint/ban-types
let i18nextLoad: Promise<Function>;

const determineLoadStrategy = (supportedLanguages: Array<string>, currentLang: string) => {
  const supportedFullLocales = supportedLanguages
    .filter(lang => lang.includes('-'))
    .map(lang => lang.toLowerCase());
  return supportedFullLocales.includes(currentLang?.toLowerCase()) ? 'currentOnly' : 'languageOnly';
};

export const i18nReact = {
  getI18nConfig: (): InitOptions => {
    const supportedLngs = ['de', 'en', 'es', 'fr', 'ja', 'ko', 'pt', 'pt-BR', 'zh', 'zh-CN'];
    const currentLang = (window as hueWindow).HUE_LANG ?? '';
    return {
      backend: { loadPath: '/static/desktop/locales/{{lng}}/{{ns}}.json' },
      lng: currentLang,
      fallbackLng: 'en',
      supportedLngs: supportedLngs,
      nonExplicitSupportedLngs: true,
      load: determineLoadStrategy(supportedLngs, currentLang),
      debug: false,
      interpolation: {
        escapeValue: false // React strings are safe from XSS
      }
    };
  },

  useTranslation: (
    nameSpace?: string | undefined,
    options?: UseTranslationOptions
  ): UseTranslationResponse<string, undefined> => {
    const config = i18nReact.getI18nConfig();
    // We need to call initialize on i18next once before we can use useTranslation hook
    if (!i18nextLoad) {
      i18nextLoad = i18next.use(HttpApi).use(initReactI18next).init(config);
    }
    return useTranslation(nameSpace, options || {});
  }
};
