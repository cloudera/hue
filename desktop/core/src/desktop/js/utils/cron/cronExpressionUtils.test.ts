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

import { explainCronExpression } from './cronExpressionUtils';

describe('cronExpressionUtils', () => {
  it('returns an empty result for blank expressions', () => {
    const result = explainCronExpression('   ');

    expect(result.isValid).toBe(false);
    expect(result.description).toBe('');
    expect(result.error).toBe('');
    expect(result.nextRuns).toEqual([]);
  });

  it('describes a valid daily cron expression', () => {
    const result = explainCronExpression('0 0 * * *');

    expect(result.isValid).toBe(true);
    expect(result.description.length).toBeGreaterThan(0);
    expect(result.nextRuns).toHaveLength(1);
  });

  it('describes weekday schedules and returns next runs', () => {
    const result = explainCronExpression('0 0/2 * * 1-5', 'UTC', { nextRunsCount: 3 });

    expect(result.isValid).toBe(true);
    expect(result.description.length).toBeGreaterThan(0);
    expect(result.nextRuns).toHaveLength(3);
  });

  it('rejects expressions that do not use the Oozie 5-field format', () => {
    const result = explainCronExpression('0 0 0 * * *');

    expect(result.isValid).toBe(false);
    expect(result.error).toContain('Expected 5 cron fields');
    expect(result.nextRuns).toEqual([]);
  });

  it('returns parser errors for invalid cron syntax', () => {
    const result = explainCronExpression('not a cron');

    expect(result.isValid).toBe(false);
    expect(result.error.length).toBeGreaterThan(0);
    expect(result.nextRuns).toEqual([]);
  });
});
