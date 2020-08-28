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

import Executable, { ExecutableRaw } from 'apps/notebook2/execution/executable';
import { syncSqlExecutables } from 'apps/notebook2/execution/utils';
import { VariableSubstitutionHandler } from 'apps/notebook2/variableSubstitution';
import { StatementDetails } from 'parse/types';
import { Compute, Connector, Namespace } from 'types/config';

export interface ExecutorRaw {
  executables: ExecutableRaw[];
}

export default class Executor {
  connector: () => Connector;
  compute: () => Compute;
  namespace: () => Namespace;
  database: () => string;
  defaultLimit?: () => number;
  isSqlEngine?: boolean;
  isOptimizerEnabled?: boolean;
  executables: Executable[] = [];
  variableSubstitionHandler?: VariableSubstitutionHandler;

  constructor(options: {
    connector: () => Connector;
    compute: () => Compute;
    namespace: () => Namespace;
    database: () => string;
    defaultLimit?: () => number;
    isSqlEngine?: boolean;
    isOptimizerEnabled?: boolean;
    executables: Executable[];
    variableSubstitionHandler?: VariableSubstitutionHandler;
  }) {
    this.connector = options.connector;
    this.compute = options.compute;
    this.namespace = options.namespace;
    this.database = options.database;
    this.isSqlEngine = options.isSqlEngine;
    this.isOptimizerEnabled = options.isOptimizerEnabled;
    this.executables = [];
    this.defaultLimit = options.defaultLimit;
    this.variableSubstitionHandler = options.variableSubstitionHandler;
  }

  toJs(): ExecutorRaw {
    return {
      executables: this.executables.map(executable => executable.toJs())
    };
  }

  cancelAll(): void {
    this.executables.forEach(existingExecutable => existingExecutable.cancelBatchChain());
  }

  setExecutables(executables: Executable[]): void {
    this.cancelAll();
    this.executables = executables;
    this.executables.forEach(executable => executable.notify());
  }

  update(statementDetails: StatementDetails, beforeExecute: boolean): Executable {
    const executables = syncSqlExecutables(this, statementDetails);

    // Cancel any "lost" executables and any batch chain it's part of
    executables.lost.forEach(lostExecutable => {
      lostExecutable.lost = true;
      lostExecutable.cancelBatchChain();
    });

    // Cancel any intersecting batch chains and create a new chain if just before execute
    if (beforeExecute) {
      executables.selected.forEach(executable => executable.cancelBatchChain());

      let previous: Executable | undefined;
      executables.selected.forEach(executable => {
        if (previous) {
          executable.previousExecutable = previous;
          previous.nextExecutable = executable;
        }
        previous = executable;
      });
    }

    // Update the executables list
    this.executables = executables.all;

    this.executables.forEach(executable => executable.notify());

    return executables.selected[0];
  }
}
