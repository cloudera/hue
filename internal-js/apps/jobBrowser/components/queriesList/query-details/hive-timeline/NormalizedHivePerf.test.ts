/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import NormalizedHivePerf from './NormalizedHivePerf';

describe('NormalizedHivePerf.ts', () => {
  it('Create with default values', () => {
    const nPerf: NormalizedHivePerf = new NormalizedHivePerf(null);
    expect(nPerf.compile).toBe(0);

    expect(nPerf.groupTotal.pre).toBe(0);
    expect(nPerf.groupTotal.submit).toBe(0);
    expect(nPerf.groupTotal.running).toBe(0);
    expect(nPerf.groupTotal.post).toBe(0);

    expect(nPerf.total).toBe(0);
  });

  it('Create with some values', () => {
    const testCompileTime = 66;
    const testTezSubmitDagTime = 99;
    const nPerf: NormalizedHivePerf = new NormalizedHivePerf({
      compile: testCompileTime,
      TezSubmitDag: testTezSubmitDagTime
    });
    expect(nPerf.compile).toBe(testCompileTime);
    expect(nPerf.TezSubmitDag).toBe(testTezSubmitDagTime);

    expect(nPerf.groupTotal.pre).toBe(testCompileTime);
    expect(nPerf.groupTotal.submit).toBe(testTezSubmitDagTime);
    expect(nPerf.groupTotal.running).toBe(0);
    expect(nPerf.groupTotal.post).toBe(0);

    expect(nPerf.total).toBe(testCompileTime + testTezSubmitDagTime);

    const nPerfDef: NormalizedHivePerf = new NormalizedHivePerf(null);
    expect(nPerfDef.compile).toBe(0);
  });
});
