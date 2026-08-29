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

import cronstrue from 'cronstrue';
import CronExpressionParser from 'cron-parser';
import { DateTime } from 'luxon';

export const OOZIE_CRON_FIELD_COUNT = 5;
export const DEFAULT_NEXT_RUNS_COUNT = 1;

export interface CronExplanation {
  isValid: boolean;
  description: string;
  error: string;
  nextRuns: string[];
}

export interface ExplainCronExpressionOptions {
  nextRunsCount?: number;
}

const formatNextRun = (date: Date, timezone?: string): string => {
  const formatted = timezone
    ? DateTime.fromJSDate(date, { zone: timezone })
    : DateTime.fromJSDate(date);

  return formatted.toFormat('ccc, LLL d, yyyy h:mm a');
};

export const explainCronExpression = (
  expression: string,
  timezone?: string,
  options?: ExplainCronExpressionOptions
): CronExplanation => {
  const trimmed = (expression || '').trim();
  const emptyResult: CronExplanation = {
    isValid: false,
    description: '',
    error: '',
    nextRuns: []
  };

  if (!trimmed) {
    return emptyResult;
  }

  const fields = trimmed.split(/\s+/);
  if (fields.length !== OOZIE_CRON_FIELD_COUNT) {
    return {
      ...emptyResult,
      error: `Expected ${OOZIE_CRON_FIELD_COUNT} cron fields (minute hour day month weekday), found ${fields.length}`
    };
  }

  try {
    const description = cronstrue.toString(trimmed, { use24HourTimeFormat: false });
    const parseOptions: { tz?: string } = {};

    if (timezone) {
      parseOptions.tz = timezone;
    }

    const interval = CronExpressionParser.parse(trimmed, parseOptions);
    const nextRuns: string[] = [];
    const nextRunsCount = options?.nextRunsCount ?? DEFAULT_NEXT_RUNS_COUNT;

    for (let i = 0; i < nextRunsCount; i++) {
      nextRuns.push(formatNextRun(interval.next().toDate(), timezone));
    }

    return {
      isValid: true,
      description,
      error: '',
      nextRuns
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Invalid cron expression';

    return {
      ...emptyResult,
      error: errorMessage
    };
  }
};

export default {
  DEFAULT_NEXT_RUNS_COUNT,
  OOZIE_CRON_FIELD_COUNT,
  explain: explainCronExpression,
  explainCronExpression
};
