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

// THIS COMPONENT WAS DIRECTLY TRANSLATED FROM VUE file
// desktop/core/src/desktop/js/components/TimeAgo.vue
// TODO: use i18nReact instead of I18n

import React from 'react';
import I18n from '../../utils/i18n';

const SECOND = { val: 1000, text: 'second' };
const MINUTE = { val: SECOND.val * 60, text: 'minute' };
const HOUR = { val: MINUTE.val * 60, text: 'hour' };
const DAY = { val: HOUR.val * 24, text: 'day' };
const MONTH = { val: DAY.val * (365 / 12), text: 'month' };
const YEAR = { val: DAY.val * 365, text: 'year' };

const LIMITS = [YEAR, MONTH, DAY, HOUR, MINUTE, SECOND];

export const timeAgo = (value: number): string => {
  const diff = Date.now() - value;
  for (const limit of LIMITS) {
    if (diff >= limit.val) {
      const val = Math.round(diff / limit.val);
      const postfix = I18n(`${limit.text}${val > 1 ? 's' : ''} ago`);
      return `${val} ${postfix}`;
    }
  }
  return I18n('now');
};

interface TimeAgoProps {
  value: number;
}

const TimeAgo: React.FC<TimeAgoProps> = ({ value }) => {
  const timeAgoValue = timeAgo(value);

  return <span>{timeAgoValue}</span>;
};

export default TimeAgo;
