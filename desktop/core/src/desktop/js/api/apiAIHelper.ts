// import MD5 from 'crypto-js/MD5';
import { hueWindow } from 'types/types';

import Executor from '../apps/editor/execution/executor';
import dataCatalog from '../catalog/dataCatalog';

const TABLES_API_URL = '/api/editor/ai/tables';
const SQL_API_URL = '/api/editor/ai/sql';

// The Error interface is based on the new Improved Hue Error UX
// specification. It is not yet implemented but lets try to follow the
// spec since it wil become the new standard.
export interface Error {
  message: string; // Error
  messageParameters?: string; // Map used to create UI specific error message from the errorCode
  errorCode?: string;
  origin?: string;
  stackTrace?: string;
  description?: string; // html format, possibly with links for docs and actionable,
}

interface GenerateExplanation {
  (params: {
    statement: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<string | { error: Error }>;
}
interface GenerateCorrectedSql {
  (params: { statement: string; dialect: string; onStatusChange: (arg: string) => void }): Promise<
    | {
        sql: string;
        explanation: string;
      }
    | { error: Error }
  >;
}

interface GenerateOptimizedSql {
  (params: {
    statement: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<
    | {
        sql: string;
        explanation: string;
      }
    | { error: Error }
  >;
}

interface GenerateSQLfromNQL {
  (params: {
    nql: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<{
    sql: string;
    assumptions: string;
  }>;
}

interface GenerateEditedSQLfromNQL {
  (params: {
    nql: string;
    sql: string;
    databaseName: string;
    executor: Executor;
    dialect: string;
    onStatusChange: (arg: string) => void;
  }): Promise<{
    sql: string;
    assumptions: string;
  }>;
}
interface GenerativeFunctionSet {
  generateExplanation: GenerateExplanation;
  generateCorrectedSql: GenerateCorrectedSql;
  generateOptimizedSql: GenerateOptimizedSql;
  generateSQLfromNQL: GenerateSQLfromNQL;
  generateEditedSQLfromNQL: GenerateEditedSQLfromNQL;
}
export function generativeFunctionFactory(): GenerativeFunctionSet {
  // TODO: Here we can conditionally use different implementations depending
  // on LLM configuration and strategy if needed;
  return {
    generateExplanation,
    generateCorrectedSql,
    generateOptimizedSql,
    generateSQLfromNQL,
    generateEditedSQLfromNQL
  };
}

interface FetchFromLlmParams {
  url: string;
  data: any;
  method?: string;
  contentType?: string;
}
const fetchFromLlm = async ({
  url,
  data,
  method = 'POST',
  contentType = 'application/json'
}: FetchFromLlmParams) => {
  const promise = fetch(url, {
    method,
    headers: {
      'Content-Type': contentType,
      'X-Csrftoken': (<hueWindow>window).CSRF_TOKEN
    },
    body: JSON.stringify(data)
  }).then(response => response.json());

  return promise;
};

const getRelevantTables = async (
  input: string,
  tableParams: getTableListParams,
  onStatusChange: (arg: string) => void
) => {
  const allTables = (await getTableList(tableParams)) as Array<string>;

  let tableMetadata = allTables;

  if (window.IS_VECTOR_DB_ENABLED) {
    tableMetadata = await getRelevantTableDetails(
      tableParams.databaseName,
      allTables,
      tableParams.executor
    );
  }

  console.info('allTables', allTables);
  onStatusChange('Finding relevant tables');

  const relevantTables = await fetchFromLlm({
    url: TABLES_API_URL,
    data: {
      input: input,
      metadata: tableMetadata,
      database: tableParams.databaseName
    }
  });

  return relevantTables;
};

const handleError = (error: any, msg: string): { error: Error } => {
  console.error(error);
  return {
    error: {
      message: msg
    }
  };
};

const fetchColumnsData = async (databaseName: string, tableName: string, executor: Executor) => {
  const dbEntry = await dataCatalog.getEntry({
    path: [databaseName, tableName],
    connector: executor.connector(),
    namespace: executor.namespace(),
    compute: executor.compute()
  });
  const columns = await dbEntry.getChildren();
  return columns;
};

export const getRelevantTableDetails = async (
  databaseName: string,
  tableNames: string[],
  executor: Executor,
  onStatusChange?: (arg: string) => void
) => {
  onStatusChange && onStatusChange('Finding relevant table metadata');
  const relevantTables = [];
  for (const tableName of tableNames) {
    const columns = await fetchColumnsData(databaseName, tableName, executor);
    const tableDetails = {
      // databaseName: databaseName,
      name: tableName,
      columns: columns.map(({ definition }) => {
        delete definition.index;
        delete definition.partitionKey;
        delete definition.primaryKey;
        return definition;
      })
    };
    relevantTables.push(tableDetails);
  }
  return relevantTables;
};

interface getTableListParams {
  databaseName: string;
  executor: Executor;
}
const getTableList = async ({ databaseName, executor }: getTableListParams) => {
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
  let relevantTables, tableMetadata;
  try {
    relevantTables = await getRelevantTables(statement, { databaseName, executor }, onStatusChange);
  } catch (e) {
    return handleError(e, 'Could not find relevant tables');
  }
  try {
    tableMetadata = await getRelevantTableDetails(databaseName, relevantTables['tables'], executor);
  } catch (e) {
    return handleError(e, 'Could not load relevant table metadata');
  }

  onStatusChange('Optimizing SQL query');

  try {
    return await fetchFromLlm({
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
    return handleError(e, 'Call to AI to optimize SQL query failed');
  }
};

const generateSQLfromNQL: GenerateSQLfromNQL = async ({
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  let relevantTables, tableMetadata;
  try {
    relevantTables = await getRelevantTables(nql, { databaseName, executor }, onStatusChange);
  } catch (e) {
    return handleError(e, 'Could not find relevant tables');
  }
  try {
    tableMetadata = await getRelevantTableDetails(
      databaseName,
      relevantTables['tables'],
      executor,
      onStatusChange
    );
  } catch (e) {
    return handleError(e, 'Could not load relevant table metadata');
  }

  onStatusChange('Generating SQL query');
  try {
    return await fetchFromLlm({
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
  } catch (e) {
    return handleError(e, 'Call to AI to generate SQL query failed');
  }
};

const generateEditedSQLfromNQL: GenerateEditedSQLfromNQL = async ({
  sql,
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  let relevantTables, tableMetadata;
  try {
    relevantTables = await getRelevantTables(
      `${sql} ${nql}`,
      { databaseName, executor },
      onStatusChange
    );
  } catch (e) {
    return handleError(e, 'Could not find relevant tables');
  }
  try {
    tableMetadata = await getRelevantTableDetails(
      databaseName,
      relevantTables['tables'],
      executor,
      onStatusChange
    );
  } catch (e) {
    return handleError(e, 'Could not load relevant table metadata');
  }

  onStatusChange('Generating SQL query');
  try {
    return await fetchFromLlm({
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
  } catch (e) {
    return handleError(e, 'Call to AI to edit SQL query failed');
  }
};

const generateExplanation: GenerateExplanation = async ({ statement, dialect, onStatusChange }) => {
  try {
    onStatusChange('Generating explanation');
    return await fetchFromLlm({
      url: SQL_API_URL,
      data: {
        task: 'summarize',
        sql: statement,
        dialect
      }
    });
  } catch (e) {
    return handleError(e, 'Call to AI to explain SQL query failed');
  }
};

const generateCorrectedSql: GenerateCorrectedSql = async ({
  statement,
  dialect,
  onStatusChange
}) => {
  onStatusChange('Generating corrected SQL query');
  try {
    return await fetchFromLlm({
      url: SQL_API_URL,
      data: {
        task: 'fix',
        sql: statement,
        dialect
      }
    });
  } catch (e) {
    return handleError(e, 'Call to AI to fix SQL query failed');
  }
};
