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

import { Session } from 'apps/editor/execution/api';
import ExecutionResult from './executionResult';
import SqlExecutable, { ExecutionStatus } from './sqlExecutable';
import ExecutionLogs from './executionLogs';

export const EXECUTABLE_TRANSITIONED_TOPIC = 'hue.executable.status.transitioned';
export interface ExecutableTransitionedEvent {
  newStatus: ExecutionStatus;
  oldStatus: ExecutionStatus;
  executable: SqlExecutable;
}

export const EXECUTABLE_UPDATED_TOPIC = 'hue.executable.updated';
export type ExecutableUpdatedEvent = SqlExecutable;

export const EXECUTABLE_LOGS_UPDATED_TOPIC = 'hue.executable.logs.updated';
export type ExecutableLogsUpdatedEvent = ExecutionLogs;

export const EXECUTABLE_RESULT_UPDATED_TOPIC = 'hue.executable.result.updated';
export type ExecutableResultUpdatedEvent = ExecutionResult;

export const SHOW_SESSION_AUTH_MODAL_TOPIC = 'show.session.auth.modal';
export interface ShowSessionAuthModalEvent {
  message?: string;
  session: Session;
  resolve(): void;
  reject(): void;
}
