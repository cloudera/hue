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

import {
  EXECUTABLE_RESULT_UPDATED_TOPIC,
  EXECUTABLE_TRANSITIONED_TOPIC,
  ExecutableResultUpdatedEvent,
  ExecutableTransitionedEvent
} from './events';
import Executor from './executor';
import { DefaultApiResponse, extractErrorMessage, post, successResponseIsError } from 'api/utils';
import SqlExecutable, {
  ExecutableContext,
  ExecutionStatus
} from 'apps/editor/execution/sqlExecutable';
import { ResultRow, ResultType } from 'apps/editor/execution/executionResult';
import { CancellablePromise } from 'api/cancellablePromise';
import SubscriptionTracker from 'components/utils/SubscriptionTracker';
import { Compute, Connector, Namespace } from 'config/types';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { getStatementsParser } from 'parse/utils';

type SessionPropertyValue = string | number | boolean | null | undefined;

export interface SessionProperty {
  defaultValue: SessionPropertyValue[];
  help_text?: string;
  key: string;
  multiple?: boolean;
  nice_name?: string;
  options?: SessionPropertyValue[];
  type?: string;
  value: SessionPropertyValue[];
}

export interface Session {
  configuration?: { [key: string]: string };
  http_addr?: string;
  id: number;
  properties: SessionProperty[];
  reuse_session?: boolean;
  session_id: string;
  type: string;
}

export interface ResultMeta {
  name: string;
  type: string;
  comment?: string | null;
}

export interface ResultApiResponse {
  data: (number | string)[][];
  has_more: boolean;
  isEscaped: boolean;
  meta: ResultMeta[];
  type: ResultType;
}

export interface ResultSizeApiResponse {
  rows: number | null;
  size: number | null;
  message?: string;
}

interface FetchResultData extends ExecutableContext {
  rows: number;
  startOver?: boolean;
}

interface FetchLogsData extends ExecutableContext {
  full_log: string;
  jobs?: string;
  from: number;
}

interface ExecuteData extends ExecutableContext {
  executable: string;
}

export interface ExecuteLogsApiResponse {
  logs: string;
  isFullLogs: boolean;
  jobs: ExecutionJob[];
}

export interface ExecutionJob {
  finished: boolean;
  name: string;
  percentJob?: number;
  started: boolean;
  url: string;
}

export interface ExecutionHandle {
  end?: { row: number; col: number };
  guid?: string;
  has_more_statements?: boolean;
  has_result_set?: boolean;
  log_context?: unknown;
  modified_row_count?: number;
  operation_type?: number;
  previous_statement_hash?: string;
  secret?: string;
  session_guid?: string;
  session_id?: number;
  session_type?: string;
  start?: { row: number; col: number };
  statement?: string;
  statement_id: number;
  statements_count?: number;
  sync?: boolean;
  result?: ResultApiResponse;
}

export interface ExecutionHistory {
  id: number;
  uuid?: string;
  parentUuid?: string;
}

export interface ExecuteApiResponse {
  handle: ExecutionHandle;
  history?: ExecutionHistory;
}

export interface ExecuteStatusApiResponse {
  result?: ResultApiResponse; // For streaming
  status: string;
  message?: string;
  has_result_set?: boolean;
}

export interface ExecuteApiOptions {
  executable: SqlExecutable;
  silenceErrors?: boolean;
}

export interface AuthRequest {
  auth: boolean;
  message?: string;
}

const CANCEL_STATEMENT_API = '/api/v1/editor/cancel_statement';
const CHECK_STATUS_API = '/api/v1/editor/check_status';
const CLOSE_SESSION_API = '/api/v1/editor/close_session';
const CLOSE_STATEMENT_API = '/api/v1/editor/close_statement';
const CREATE_SESSION_API = '/api/v1/editor/create_session';
const EXECUTE_API_PREFIX = '/api/v1/editor/execute/';
const FETCH_RESULT_DATA_API = '/api/v1/editor/fetch_result_data';
const FETCH_RESULT_SIZE_API = '/api/v1/editor/fetch_result_size';
const GET_LOGS_API = '/api/v1/editor/get_logs';

export const createSession = async (options: {
  type: string;
  properties?: SessionProperty[];
  silenceErrors?: boolean;
}): Promise<AuthRequest | Session> => {
  const data = {
    session: JSON.stringify({ type: options.type, properties: options.properties || [] })
  };

  const responsePromise = post<
    {
      session?: Session;
      status: number;
      message?: string;
    },
    { session: string }
  >(CREATE_SESSION_API, data, {
    silenceErrors: !!options.silenceErrors,
    ignoreSuccessErrors: true
  });

  const response = await responsePromise;
  if (response.status === 401) {
    return { auth: true, message: response.message };
  }
  if (successResponseIsError(response)) {
    throw new Error(extractErrorMessage(response));
  }

  if (!response.session) {
    throw new Error('No session returned.');
  }
  return response.session;
};

export const closeSession = async (options: {
  session: Session;
  silenceErrors?: boolean;
}): Promise<void> => {
  const data = {
    session: JSON.stringify(options.session)
  };

  await post<void, { session: string }>(CLOSE_SESSION_API, data, {
    silenceErrors: !!options.silenceErrors
  });
};

export const executeStatement = async (options: ExecuteApiOptions): Promise<ExecuteApiResponse> => {
  const executable = options.executable;
  const url = EXECUTE_API_PREFIX + executable.executor.connector().dialect;

  const data = (await executable.toContext()) as ExecuteData;
  data.executable = executable.toJson();

  const executePromise = post<
    {
      handle: ExecutionHandle;
      history_id?: number;
      history_uuid?: string;
      history_parent_uuid?: string;
      result?: ResultApiResponse;
    },
    ExecuteData
  >(url, data, {
    silenceErrors: !!options.silenceErrors
  });

  executable.addCancellable({
    cancel: async () => {
      if (
        executable.status !== ExecutionStatus.running &&
        executable.status !== ExecutionStatus.streaming
      ) {
        // executable.status seems to have been set to 'canceling' so ignoring for now
        // return;
      }
      try {
        const response = await executePromise;
        if (options.executable.handle !== response.handle) {
          options.executable.handle = response.handle;
        }
        if (response.handle) {
          await cancelStatement(options);
        }
      } catch (err) {}
    }
  });

  const response = await executePromise;

  if (!response.handle) {
    throw new Error('No handle in execute response');
  }

  response.handle.result = response.result;

  const cleanedResponse: ExecuteApiResponse = {
    handle: response.handle
  };

  if (typeof response.history_id !== 'undefined') {
    cleanedResponse.history = {
      id: response.history_id,
      uuid: response.history_uuid,
      parentUuid: response.history_parent_uuid
    };
  }

  return cleanedResponse;
};

export const executeSingleStatement = ({
  database = 'default',
  connector,
  namespace,
  compute,
  statement
}: {
  connector: Connector;
  namespace: Namespace;
  compute: Compute;
  statement: string;
  database?: string;
}): CancellablePromise<{ meta?: ResultMeta[]; rows?: ResultRow[] }> => {
  const subTracker = new SubscriptionTracker();

  const promise = new CancellablePromise<{
    meta: ResultMeta[];
    rows: ResultRow[];
  }>((resolve, reject, onCancel) => {
    onCancel(() => reject('Cancelled'));

    const executor = new Executor({
      database: (() => database) as KnockoutObservable<string>,
      connector: (() => connector) as KnockoutObservable<Connector>,
      namespace: (() => namespace) as KnockoutObservable<Namespace>,
      compute: (() => compute) as KnockoutObservable<Compute>
    });

    let parsedStatement: ParsedSqlStatement | undefined = undefined;

    try {
      const parsedStatements = getStatementsParser(connector).parse(statement);
      parsedStatement = parsedStatements[0];
    } catch {}

    if (!parsedStatement) {
      reject('Failed parsing statement');
      return;
    }
    const sqlExecutable = new SqlExecutable({ executor, database, parsedStatement });
    executor.setExecutables([sqlExecutable]);

    subTracker.subscribe<ExecutableTransitionedEvent>(
      EXECUTABLE_TRANSITIONED_TOPIC,
      ({ executable, newStatus }) => {
        if (executable.id === sqlExecutable.id && newStatus === ExecutionStatus.failed) {
          reject('Execution failed.');
        } else if (
          executable.isSuccess() &&
          executable.handle &&
          !executable.handle.has_result_set
        ) {
          resolve();
        }
      }
    );

    subTracker.subscribe<ExecutableResultUpdatedEvent>(
      EXECUTABLE_RESULT_UPDATED_TOPIC,
      executionResult => {
        const { executable, rows, meta } = executionResult;
        if (executable.id === sqlExecutable.id && rows.length) {
          resolve({ rows, meta });
        }
      }
    );

    subTracker.addDisposable({
      dispose() {
        sqlExecutable.cancel().catch();
      }
    });

    sqlExecutable.execute().catch(reject);
  });

  promise.finally(() => {
    subTracker.dispose();
  });

  return promise;
};

export const cancelStatement = async (options: ExecuteApiOptions): Promise<void> => {
  const data = await options.executable.toContext();

  await post<void, ExecutableContext>(CANCEL_STATEMENT_API, data, {
    silenceErrors: !!options.silenceErrors
  });
};

export const closeStatement = async (options: ExecuteApiOptions): Promise<void> => {
  if (!options.executable.operationId) {
    return;
  }
  const data = { operationId: options.executable.operationId };
  await post<void, { operationId: string }>(CLOSE_STATEMENT_API, data, {
    silenceErrors: !!options.silenceErrors
  });
};

export const checkExecutionStatus = async (
  options: ExecuteApiOptions
): Promise<ExecuteStatusApiResponse> => {
  if (!options.executable.operationId) {
    throw new Error('No operationId given.');
  }

  const data = { operationId: options.executable.operationId };
  const responsePromise = post<
    {
      query_status?: ExecuteStatusApiResponse;
      status: number;
      message?: string;
    },
    { operationId: string }
  >(CHECK_STATUS_API, data, {
    silenceErrors: !!options.silenceErrors
  });

  options.executable.addCancellable(responsePromise);

  const response = await responsePromise;

  if (response.query_status) {
    return response.query_status;
  }

  if (response.status === -3) {
    return { status: ExecutionStatus.expired };
  }

  return { status: ExecutionStatus.failed, message: response.message };
};

export const fetchResults = async (options: {
  executable: SqlExecutable;
  rows: number;
  startOver?: boolean;
  silenceErrors?: boolean;
}): Promise<ResultApiResponse | undefined> => {
  const data = (await options.executable.toContext()) as FetchResultData;
  data.rows = options.rows;
  data.startOver = options.startOver;

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const transformResponse = (response: unknown) => JSON.bigdataParse(response);

  const response = await post<DefaultApiResponse & { result?: ResultApiResponse }>(
    FETCH_RESULT_DATA_API,
    data,
    {
      silenceErrors: !!options.silenceErrors,
      transformResponse
    }
  );

  return response.result;
};

export const fetchResultSize = async (
  options: ExecuteApiOptions
): Promise<ResultSizeApiResponse> => {
  const data = await options.executable.toContext();

  const responsePromise = post<
    {
      result: ResultSizeApiResponse;
    },
    ExecutableContext
  >(FETCH_RESULT_SIZE_API, data, {
    silenceErrors: !!options.silenceErrors
  });

  options.executable.addCancellable(responsePromise);
  const response = await responsePromise;
  return response.result;
};

export const fetchLogs = async (options: {
  executable: SqlExecutable;
  silenceErrors?: boolean;
  fullLog: string;
  jobs?: ExecutionJob[];
  from?: number;
}): Promise<ExecuteLogsApiResponse> => {
  const data = (await options.executable.toContext()) as FetchLogsData;
  data.full_log = options.fullLog;
  data.jobs = options.jobs && JSON.stringify(options.jobs);
  data.from = options.from || 0;

  const responsePromise = post<
    {
      logs: string;
      isFullLogs: boolean;
      jobs: ExecutionJob[];
      progress: number;
      status: number;
      message?: string;
    },
    FetchLogsData
  >(GET_LOGS_API, data, {
    silenceErrors: !!options.silenceErrors
  });

  options.executable.addCancellable(responsePromise);
  const response = await responsePromise;
  return {
    logs: (response.status === 1 && response.message) || response.logs || '',
    jobs: response.jobs || [],
    isFullLogs: response.isFullLogs
  };
};
