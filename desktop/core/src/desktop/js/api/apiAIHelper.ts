/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import { post } from '../api/utils';
import Executor from '../apps/editor/execution/executor';
import dataCatalog from '../catalog/dataCatalog';
import { ExtendedColumn } from '../catalog/DataCatalogEntry';

import HueError from './HueError';

const TABLES_API_URL = '/api/v1/editor/ai/tables';
const SQL_API_URL = '/api/v1/editor/ai/sql';

export interface TableColumnsMetadataItem {
  columns: Array<ExtendedColumn>;
  dbName: string;
  name: string;
}

export type TableColumnsMetadata = Array<TableColumnsMetadataItem>;

interface ExplainSqlResponse {
  explain: string;
  summary: string;
}
interface GenerateExplanation {
  (params: {
    statement: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<ExplainSqlResponse>;
}

interface CorrectSqlResponse {
  sql: string;
  explanation: string;
}
interface GenerateCorrectedSql {
  (params: {
    statement: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<CorrectSqlResponse>;
}

interface CommentedSqlResponse {
  sql: string;
}
interface GenerateCommentedSql {
  (params: {
    statement: string;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<CommentedSqlResponse>;
}

interface OptimizeSqlResponse {
  sql: string;
  explanation: string;
}
interface GenerateOptimizedSql {
  (params: {
    statement: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<OptimizeSqlResponse>;
}

interface GenerateSqlResponse {
  sql: string;
  assumptions: string;
  tableColumnsMetadata?: TableColumnsMetadata;
}
interface GenerateSQLfromNQL {
  (params: {
    nql: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<GenerateSqlResponse>;
}

interface EditSQLResponse {
  sql: string;
  assumptions: string;
  tableColumnsMetadata?: TableColumnsMetadata;
}
interface GenerateEditedSQLfromNQL {
  (params: {
    nql: string;
    previousNql?: string;
    tableNamesUsed?: string[];
    sql: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<EditSQLResponse>;
}
interface GenerativeFunctionSet {
  generateExplanation: GenerateExplanation;
  generateCorrectedSql: GenerateCorrectedSql;
  generateOptimizedSql: GenerateOptimizedSql;
  generateSQLfromNQL: GenerateSQLfromNQL;
  generateEditedSQLfromNQL: GenerateEditedSQLfromNQL;
  generateCommentedSql: GenerateCommentedSql;
}
export function generativeFunctionFactory(): GenerativeFunctionSet {
  // TODO: Here we can conditionally use different implementations depending
  // on LLM configuration and strategy if needed;
  return {
    generateExplanation,
    generateCorrectedSql,
    generateOptimizedSql,
    generateSQLfromNQL,
    generateEditedSQLfromNQL,
    generateCommentedSql
  };
}

interface FetchFromLlmParams {
  url: string;
  data: unknown;
  method?: string;
  contentType?: string;
}
const fetchFromLlm = async <T>({ url, data }: FetchFromLlmParams): Promise<T> => {
  return post(url, data, { qsEncodeData: false, silenceErrors: true }).catch(error => {
    // The error is already a HueError so we can just rethrow it.
    if (error instanceof HueError) {
      throw error;
    }
    // When there is no HueError we throw one with the original error as cause
    // in order for this function to provide a consistent Error API.
    throw new HueError(error.message, { cause: error });
  }) as Promise<T>;
};

const augmentError = (e: unknown, defaultMsg: string): HueError => {
  const error =
    e instanceof HueError
      ? e
      : new HueError(defaultMsg, { cause: e instanceof Error ? e : undefined });

  // If the API is follwing the new improved Error spec there will be a descriptive
  // error message present. If not we will use the default message.
  if (!error.message) {
    error.message = defaultMsg;
    console.error(error);
  }

  return error;
};

const getTablesAndMetadata = async (
  input: string,
  databaseName: string,
  executor: Executor,
  onStatusChange: (arg: string) => void
) => {
  const relevantTables = await getRelevantTables(input, { databaseName, executor }, onStatusChange);
  let tableMetadata;
  try {
    onStatusChange('Retrieving table metadata');
    tableMetadata = await getRelevantTableDetails(databaseName, relevantTables['tables'], executor);
  } catch (e) {
    throw new HueError('Could not load relevant table metadata');
  }
  return { relevantTables, tableMetadata };
};

interface RelevantTablesResponse {
  tables: string[];
}
const getRelevantTables = async (
  input: string,
  tableParams: getTableListParams,
  onStatusChange: (arg: string) => void
): Promise<RelevantTablesResponse> => {
  onStatusChange('Retrieving all table names');
  let allTables;
  try {
    allTables = (await getTableList(tableParams)) as Array<string>;
  } catch (e) {
    throw augmentError(e, 'Failed loading table names');
  }

  if (!Array.isArray(allTables) || allTables.length === 0) {
    throw new HueError('No tables found. Please verify DB name used.');
  }

  onStatusChange('Filtering relevant tables');
  let relevantTables;
  try {
    relevantTables = await fetchFromLlm<RelevantTablesResponse>({
      url: TABLES_API_URL,
      data: {
        input: input,
        metadata: allTables,
        database: tableParams.databaseName
      }
    });
  } catch (e) {
    throw augmentError(e, 'Error filtering relevant tables.');
  }

  const tablesList = relevantTables?.tables;
  if (!Array.isArray(tablesList) || tablesList.length === 0) {
    throw new HueError('Could not find any relevant tables.');
  }

  return relevantTables;
};

const fetchColumnsData = async (databaseName: string, tableName: string, executor: Executor) => {
  const dbEntry = await dataCatalog.getEntry({
    path: [databaseName, tableName],
    connector: executor.connector(),
    namespace: executor.namespace(),
    compute: executor.compute()
  });

  const type = dbEntry.definition?.type;
  const comment = dbEntry.definition?.comment;

  const foreignKeys = dbEntry.sourceMeta?.foreign_keys.map(keyDetails => {
    const toParts = keyDetails.to.split('.');
    return {
      fromColumn: keyDetails.name,
      toColumn: toParts.pop(),
      toTable: toParts.join('.')
    };
  });

  const children = await dbEntry.getChildren();
  return {
    dbName: databaseName,
    name: tableName,
    type,
    comment,
    columns: children
      .map(({ definition }) => {
        return definition as ExtendedColumn;
      })
      .filter(def => def !== undefined),
    partitions: children.partitions,
    foreignKeys: foreignKeys || []
  };
};

export const getRelevantTableDetails = async (
  databaseName: string,
  tableNames: string[],
  executor: Executor,
  onStatusChange?: (arg: string) => void
): Promise<Array<TableColumnsMetadataItem>> => {
  onStatusChange && onStatusChange('Finding relevant table metadata');
  const relevantTables = [];
  for (const tableName of tableNames) {
    try {
      const tableDetails = await fetchTableDetails(databaseName, tableName, executor);
      relevantTables.push(tableDetails);
    } catch (error) {
      console.error(`Could not fetch columns data for table: ${tableName}`, error);
      continue;
    }
  }

  return relevantTables;
};

interface getTableListParams {
  databaseName: string;
  executor: Executor;
}
const getTableList = async ({ databaseName, executor }: getTableListParams) => {
  if (!databaseName) {
    throw new HueError('Filed to load tables. Missing database.');
  }
  const dbEntry = await dataCatalog.getEntry({
    path: databaseName,
    connector: executor?.connector(),
    namespace: executor?.namespace(),
    compute: executor?.compute()
  });
  const dbChildren = await dbEntry.getChildren();
  const tableNames = dbChildren.map(({ name }) => name);
  return tableNames;
};

const generateOptimizedSql: GenerateOptimizedSql = async ({
  statement,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  let tableMetadata;
  try {
    ({ tableMetadata } = await getTablesAndMetadata(
      statement,
      databaseName,
      executor,
      onStatusChange
    ));
  } catch (e) {
    throw augmentError(e, 'Could not find relevant tables');
  }

  onStatusChange('Optimizing SQL query');

  try {
    return await fetchFromLlm<OptimizeSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'optimize',
        sql: statement,
        dialect,
        metadata: {
          tables: tableMetadata
        }
      }
    });
  } catch (e) {
    throw augmentError(e, 'Call to AI to optimize SQL query failed');
  }
};

const generateSQLfromNQL: GenerateSQLfromNQL = async ({
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  let tableMetadata;
  try {
    ({ tableMetadata } = await getTablesAndMetadata(nql, databaseName, executor, onStatusChange));
  } catch (e) {
    throw augmentError(e, 'Could not find relevant tables');
  }

  onStatusChange('Generating SQL query');
  try {
    const result = await fetchFromLlm<GenerateSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'generate',
        input: nql,
        dialect,
        metadata: {
          tables: tableMetadata
        }
      }
    });
    return { ...result, tableColumnsMetadata: tableMetadata };
  } catch (e) {
    throw augmentError(e, 'Call to AI to generate SQL query failed ');
  }
};

const generateEditedSQLfromNQL: GenerateEditedSQLfromNQL = async ({
  sql,
  nql,
  previousNql,
  tableNamesUsed,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  let tableMetadata;
  try {
    const tables = tableNamesUsed?.join(' ') || '';
    const inputForTableList = `${tables} ${previousNql || ''} ${nql}`;
    ({ tableMetadata } = await getTablesAndMetadata(
      inputForTableList,
      databaseName,
      executor,
      onStatusChange
    ));
  } catch (e) {
    throw augmentError(e, 'Could not find relevant tables');
  }

  onStatusChange('Generating SQL query');
  try {
    const result = await fetchFromLlm<EditSQLResponse>({
      url: SQL_API_URL,
      data: {
        task: 'edit',
        sql,
        input: nql,
        dialect,
        metadata: {
          tables: tableMetadata
        }
      }
    });
    return { ...result, tableColumnsMetadata: tableMetadata };
  } catch (e) {
    throw augmentError(e, 'Call to AI to edit SQL query failed');
  }
};

const generateExplanation: GenerateExplanation = async ({
  statement,
  dialect,
  databaseName,
  executor,
  onStatusChange
}) => {
  try {
    let tableMetadata;
    try {
      ({ tableMetadata } = await getTablesAndMetadata(
        statement,
        databaseName,
        executor,
        onStatusChange
      ));
    } catch (e) {
      throw augmentError(e, 'Could not find relevant tables');
    }

    onStatusChange('Generating explanation');
    return await fetchFromLlm<ExplainSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'summarize',
        sql: statement,
        dialect,
        metadata: {
          tables: tableMetadata
        }
      }
    });
  } catch (e) {
    throw augmentError(e, 'Call to AI to explain SQL query failed');
  }
};

const generateCorrectedSql: GenerateCorrectedSql = async ({
  statement,
  dialect,
  databaseName,
  executor,
  onStatusChange
}) => {
  let tableMetadata;
  try {
    ({ tableMetadata } = await getTablesAndMetadata(
      statement,
      databaseName,
      executor,
      onStatusChange
    ));
  } catch (e) {
    throw augmentError(e, 'Could not find relevant tables');
  }

  onStatusChange('Generating corrected SQL query');
  try {
    return await fetchFromLlm<CorrectSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'fix',
        sql: statement,
        dialect,
        metadata: {
          tables: tableMetadata
        }
      }
    });
  } catch (e) {
    throw augmentError(e, 'Call to AI to fix SQL query failed');
  }
};

const generateCommentedSql: GenerateCommentedSql = async ({
  statement,
  dialect,
  onStatusChange
}) => {
  onStatusChange('Generating comments for SQL query');
  try {
    return await fetchFromLlm<CorrectSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'comment',
        sql: statement,
        dialect
      }
    });
  } catch (e) {
    throw augmentError(e, 'Call to AI to comment SQL query failed');
  }
};
