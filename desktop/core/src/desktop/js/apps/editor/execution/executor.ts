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

import KnockoutObservable from '@types/knockout';

import Snippet from 'apps/editor/snippet';
import SqlExecutable, { ExecutableRaw } from 'apps/editor/execution/sqlExecutable';
import { syncSqlExecutables } from 'apps/editor/execution/utils';
import { StatementDetails } from 'parse/types';
import { Compute, Connector, Namespace } from 'config/types';
import { VariableIndex } from 'apps/editor/components/variableSubstitution/types';

export interface ExecutorRaw {
  executables: ExecutableRaw[];
}

export interface ExecutorOptions {
  connector: KnockoutObservable<Connector>;
  compute: KnockoutObservable<Compute>;
  namespace: KnockoutObservable<Namespace>;
  database: KnockoutObservable<string>;
  defaultLimit?: KnockoutObservable<number>;
  isSqlEngine?: boolean;
  snippet?: Snippet;
  isSqlAnalyzerEnabled?: boolean;
}

export default class Executor {
  connector: KnockoutObservable<Connector>;
  compute: KnockoutObservable<Compute>;
  namespace: KnockoutObservable<Namespace>;
  database: KnockoutObservable<string>;
  defaultLimit?: KnockoutObservable<number>;
  isSqlEngine?: boolean;
  isSqlAnalyzerEnabled?: boolean;
  executables: SqlExecutable[] = [];
  snippet?: Snippet;
  activeExecutable?: SqlExecutable;
  variables: VariableIndex = {};

  constructor(options: ExecutorOptions) {
    this.connector = options.connector;
    this.compute = options.compute;
    this.namespace = options.namespace;
    this.database = options.database;
    this.isSqlEngine = options.isSqlEngine;
    this.isSqlAnalyzerEnabled = options.isSqlAnalyzerEnabled;
    this.executables = [];
    this.defaultLimit = options.defaultLimit;
    this.snippet = options.snippet;
  }

  toJs(): ExecutorRaw {
    return {
      executables: this.executables.map(executable => executable.toJs())
    };
  }

  cancelAll(): void {
    this.executables.forEach(existingExecutable => existingExecutable.cancelBatchChain());
  }

  setExecutables(executables: SqlExecutable[]): void {
    this.cancelAll();
    this.executables = executables;
    this.executables.forEach(executable => executable.notify());
  }

  update(statementDetails: StatementDetails, beforeExecute: boolean): SqlExecutable {
    const executables = syncSqlExecutables(this, statementDetails);

    // Cancel any "lost" executables and any batch chain it's part of
    executables.lost.forEach(lostExecutable => {
      lostExecutable.lost = true;
      lostExecutable.cancelBatchChain();
    });

    // Cancel any intersecting batch chains and create a new chain if just before execute
    if (beforeExecute) {
      executables.selected.forEach(executable => executable.cancelBatchChain());

      let previous: SqlExecutable | undefined;
      executables.selected.forEach(executable => {
        if (previous) {
          executable.previousExecutable = previous;
          previous.nextExecutable = executable;
        }
        previous = executable;
      });
    }

    // Update the executables list
    this.activeExecutable = executables.active;
    this.executables = executables.all;

    this.executables.forEach(executable => executable.notify());

    return executables.selected[0];
  }
}
