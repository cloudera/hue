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

import Snippet from 'apps/editor/snippet';
import Executable, { ExecutableRaw } from 'apps/editor/execution/executable';
import { StatementDetails } from 'parse/types';
import { Compute, Connector, Namespace } from 'types/config';
import { VariableIndex } from 'apps/editor/components/variableSubstitution/types';

export interface ExecutorRaw {
  executables: ExecutableRaw[];
}

export default class Executor {
  connector: KnockoutObservable<Connector>;
  compute: KnockoutObservable<Compute>;
  namespace: KnockoutObservable<Namespace>;
  database: KnockoutObservable<string>;
  defaultLimit?: KnockoutObservable<number>;
  isSqlEngine?: boolean;
  isOptimizerEnabled?: boolean;
  executables: Executable[];
  snippet?: Snippet;
  activeExecutable?: Executable;
  variables: VariableIndex;

  constructor(options: {
    connector: KnockoutObservable<Connector>;
    compute: KnockoutObservable<Compute>;
    namespace: KnockoutObservable<Namespace>;
    database: KnockoutObservable<string>;
    defaultLimit?: KnockoutObservable<number>;
    isSqlEngine?: boolean;
    snippet?: Snippet;
    isOptimizerEnabled?: boolean;
  });

  toJs(): ExecutorRaw;
  cancelAll(): void;
  setExecutables(executables: Executable[]): void;
  update(statementDetails: StatementDetails, beforeExecute: boolean): Executable;
}
