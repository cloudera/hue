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

import { Perf } from '../..';

export default class NormalizedHivePerf {
  compile = 0;
  parse = 0;
  TezBuildDag = 0;

  TezSubmitDag = 0;
  TezSubmitToRunningDag = 0;

  TezRunDag = 0;

  PostHiveProtoLoggingHook = 0;
  RemoveTempOrDuplicateFiles = 0;
  RenameOrMoveFiles = 0;

  groupTotal: {
    pre: number;
    submit: number;
    running: number;
    post: number;
  };
  total: number;

  constructor(perf: Perf | undefined) {
    perf = perf || {};
    Object.assign(this, perf);

    this.PostHiveProtoLoggingHook =
      perf['PostHook.org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook'] || 0;

    this.groupTotal = {
      pre: this.compile + this.parse + this.TezBuildDag,
      submit: this.TezSubmitDag + this.TezSubmitToRunningDag,
      running: this.TezRunDag,
      post: this.PostHiveProtoLoggingHook + this.RemoveTempOrDuplicateFiles + this.RenameOrMoveFiles
    };

    this.total =
      this.groupTotal.pre + this.groupTotal.submit + this.groupTotal.running + this.groupTotal.post;
  }
}
