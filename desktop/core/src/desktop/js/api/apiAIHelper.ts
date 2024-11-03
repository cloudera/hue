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

import { post, get } from '../api/utils';
import Executor from '../apps/editor/execution/executor';
import dataCatalog from '../catalog/dataCatalog';
import { ExtendedColumn } from '../catalog/DataCatalogEntry';
import { HistoryItem } from '../apps/editor/components/AiAssist/AiAssistToolbar/AiAssistToolbarHistory';
import HueError from './HueError';

const DBS_API_URL = '/api/v1/editor/ai/dbs';
const SQL_API_URL = '/api/v1/editor/ai/sql';

export interface TableDetails {
  columns: Array<ExtendedColumn>;
  dbName: string;
  name: string;
}

export interface DbTableDetails {
  name: string;
  tables: TableDetails[];
}

export type TableColumnsMetadata = Array<TableDetails>;

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

interface DbTableDetailsParams {
  input: string;
  databaseNames: string[];
  executor: Executor;
  onStatusChange: (arg: string) => void;
}
const getDbTableDetails = async ({
  input,
  databaseNames,
  executor,
  onStatusChange
}: DbTableDetailsParams): Promise<DbTableDetails[]> => {
  try {
    const dbTables = await getRelevantDbTables({
      input,
      databaseNames,
      executor,
      onStatusChange
    });

    onStatusChange('Retrieving table details');
    const dbTableDetails: DbTableDetails[] = [];
    for (const db of dbTables) {
      const tableDetails = await getTableDetails(db.name, db.tables, executor);
      dbTableDetails.push({
        name: db.name,
        tables: tableDetails
      });
    }

    return dbTableDetails;
  } catch (e) {
    throw augmentError(e, 'Could not find relevant tables');
  }
};

interface DbTableNames {
  name: string;
  tables: string[];
}
interface GetRelevantMetadataParams {
  input: string;
  databaseNames: string[];
  executor: Executor;
  onStatusChange: (arg: string) => void;
}
const getRelevantDbTables = async ({
  input,
  databaseNames,
  executor,
  onStatusChange
}: GetRelevantMetadataParams): Promise<DbTableNames[]> => {
  onStatusChange('Retrieving all table names');
  const metadata = [];

  for (const dbName of databaseNames) {
    let allTables;
    try {
      allTables = (await getTableList(dbName, executor)) as Array<string>;
    } catch (e) {
      throw augmentError(e, 'Failed loading table names');
    }

    metadata.push({
      name: dbName,
      tables: allTables
    });
  }

  onStatusChange('Filtering relevant tables');
  try {
    const response = await fetchFromLlm<{
      dbs: DbTableNames[];
    }>({
      url: DBS_API_URL,
      data: {
        input: input,
        dbs: metadata
      }
    });

    return response.dbs;
  } catch (e) {
    throw augmentError(e, 'Error filtering relevant tables.');
  }
};

const fetchTableDetails = async (databaseName: string, tableName: string, executor: Executor) => {
  const dbEntry = await dataCatalog.getEntry({
    path: [databaseName, tableName],
    connector: executor.connector(),
    namespace: executor.namespace(),
    compute: executor.compute()
  });

  const type = dbEntry.definition?.type;
  const comment = dbEntry.definition?.comment;

  const foreignKeys = dbEntry.sourceMeta?.foreign_keys?.map(keyDetails => {
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

export const getTableDetails = async (
  databaseName: string,
  tableNames: string[],
  executor: Executor,
  onStatusChange?: (arg: string) => void
): Promise<TableDetails[]> => {
  onStatusChange && onStatusChange('Fetching relevant table details');

  const tableDetails = [];
  for (const tableName of tableNames) {
    try {
      tableDetails.push(await fetchTableDetails(databaseName, tableName, executor));
    } catch (error) {
      const msg = `Could not fetch columns data for table: ${tableName}`;
      console.error(msg, error);
      throw new HueError(msg);
    }
  }

  return tableDetails;
};

const getTableList = async (databaseName: string, executor: Executor) => {
  if (!databaseName) {
    throw new HueError('Failed to load tables. Missing database selection.');
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
  const dbTableDetails = await getDbTableDetails({
    input: statement,
    databaseNames: [databaseName],
    executor,
    onStatusChange
  });

  onStatusChange('Optimizing SQL query');

  try {
    return await fetchFromLlm<OptimizeSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'optimize',
        sql: statement,
        dialect,
        metadata: {
          dbs: dbTableDetails
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
  const dbTableDetails = await getDbTableDetails({
    input: nql,
    databaseNames: [databaseName],
    executor,
    onStatusChange
  });

  onStatusChange('Generating SQL query');
  try {
    const result = await fetchFromLlm<GenerateSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'generate',
        input: nql,
        dialect,
        metadata: {
          dbs: dbTableDetails
        }
      }
    });
    // TODO: Make tableColumnsMetadata work for all DBs
    return { ...result, tableColumnsMetadata: dbTableDetails[0].tables };
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
  const tables = tableNamesUsed?.join(' ') || '';
  const inputForTableList = `${tables} ${previousNql || ''} ${nql}`;
  const dbTableDetails = await getDbTableDetails({
    input: inputForTableList,
    databaseNames: [databaseName],
    executor,
    onStatusChange
  });

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
          dbs: dbTableDetails
        }
      }
    });

    // TODO: Make tableColumnsMetadata work for all DBs
    return { ...result, tableColumnsMetadata: dbTableDetails[0].tables };
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
    const dbTableDetails = await getDbTableDetails({
      input: statement,
      databaseNames: [databaseName],
      executor,
      onStatusChange
    });

    onStatusChange('Generating explanation');
    return await fetchFromLlm<ExplainSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'summarize',
        sql: statement,
        dialect,
        metadata: {
          dbs: dbTableDetails
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
  const dbTableDetails = await getDbTableDetails({
    input: statement,
    databaseNames: [databaseName],
    executor,
    onStatusChange
  });

  onStatusChange('Generating corrected SQL query');
  try {
    return await fetchFromLlm<CorrectSqlResponse>({
      url: SQL_API_URL,
      data: {
        task: 'fix',
        sql: statement,
        dialect,
        metadata: {
          dbs: dbTableDetails
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

// Function to fetch history items from the API
export const getHistoryItems = async (
  databaseName: string,
  dialect: string
): Promise<HistoryItem[]> => {
  try {
    const response = await get('/api/v1/editor/ai/prompts', {
      databaseName: databaseName,
      dialect: dialect
    });
    return response as HistoryItem[];
  } catch (error) {
    console.error('Error fetching history items:', error);
    return [];
  }
};

export const createHistoryItem = async (promptItem: HistoryItem): Promise<HistoryItem> => {
  try {
    const response = await post('/api/v1/editor/ai/prompt/create', promptItem);
    return response as HistoryItem;
  } catch (error) {
    console.error('Error creating history items:', error);
    return {} as HistoryItem;
  }
};

export const updateHistoryItem = async (promptItem: HistoryItem): Promise<HistoryItem> => {
  try {
    const response = await post('/api/v1/editor/ai/prompt/update', promptItem);
    return response as HistoryItem;
  } catch (error) {
    console.error('Error updating history items:', error);
    return {} as HistoryItem;
  }
};
