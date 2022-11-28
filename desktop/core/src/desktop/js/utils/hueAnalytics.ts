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

import { getLastKnownConfig } from '../config/hueConfig';
import { post } from '../api/utils';
import { hueWindow } from '../types/types';

// HOW TO TRACK EVENTS
// a) Calling the hueAnalytics.log or hueAnalytics.convert manually
// b) Using the attribute "data-hue-analytics" on a clickable HTML element
// and set a string value containing the area followed by a colon and the action e.g.
// <a href="#" data-hue-analytics="metastore:remove stuff">Remove</a>
//
// Setting the additional attribute data-hue-analytics-prio="true" will cause the interaction
// to be logged in the Hue backend, independent of the collect_usage setting. This should be used
// with caution to prevent flooding the log.

const formatGaData = (
  area: string,
  action: string
): { type: string; name: string; params: { action: string; version: string } } => ({
  type: 'event',
  name: area,
  params: {
    action,
    version: (<hueWindow>window).HUE_VERSION || ''
  }
});

// Check and warning for when the analytics log/convert are called incorrectly
// by legacy non typescript code. We want this to fail silenctly in hueDebugAnalytics mode.
const validateParameterTypes = (area: string, action: string): boolean => {
  const typedWindow = <hueWindow>window;
  if (typedWindow.DEV && typedWindow.hueDebugAnalytics) {
    if (typeof area !== 'string') {
      console.error(`hueAnalytics parameter "area" must be a string`);
    }
    if (typeof action !== 'string') {
      console.error(`hueAnalytics parameter "action" must be a string`);
    }
  }

  return typeof area === 'string' && typeof action === 'string';
};

export const hueAnalytics = {
  log(area: string, action: string, isPrioritised?: boolean): void {
    const config = getLastKnownConfig();
    const typedWindow = <hueWindow>window;
    if (isPrioritised) {
      this.convert(area, action);
    }

    if (config?.hue_config?.collect_usage) {
      if (!validateParameterTypes(area, action)) {
        return;
      }

      const { type, name, params } = formatGaData(area, action);

      // Quick debug mode to check that the analytics logging is working when developing new features
      // Turn on by typing "window.hueDebugAnalytics = true;" in the browser JS console or setting
      // "window.hueDebugAnalytics = true" in hue.js;
      if (typedWindow.DEV && typedWindow.hueDebugAnalytics) {
        console.info('Analytics debug:', type, name, params);
      }

      if (!typedWindow.DEV) {
        typedWindow.gtag?.(type, name, params);
      }
    }
  },
  convert(area: string, action: string): void {
    if (!validateParameterTypes(area, action)) {
      return;
    }

    post('/desktop/log_analytics', {
      area,
      action
    });
  }
};

export const setupGlobalListenersForAnalytics = (): void => {
  document.addEventListener('click', event => {
    const eventTarget = event?.target as HTMLElement;
    const analyticsDataAttribute = eventTarget.dataset?.hueAnalytics;
    if (analyticsDataAttribute) {
      const [area, action] = analyticsDataAttribute.split(':');
      const isPrioritised = !!eventTarget.dataset.hueAnalyticsPrio;
      return hueAnalytics.log(area, action, isPrioritised);
    }
  });
};

export default hueAnalytics;
