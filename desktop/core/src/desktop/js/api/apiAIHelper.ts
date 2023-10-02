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

const getTablesAndMetadata = async (
  input: string,
  databaseName: string,
  executor: Executor,
  onStatusChange: (arg: string) => void
) => {
  let relevantTables, tableMetadata;

  relevantTables = await getRelevantTables(input, { databaseName, executor }, onStatusChange);
  try {
    onStatusChange('Retrieving table metadata');
    tableMetadata = await getRelevantTableDetails(databaseName, relevantTables['tables'], executor);
  } catch (e) {
    throw new Error('Could not load relevant table metadata');
  }
  return { relevantTables, tableMetadata };
};

const getRelevantTables = async (
  input: string,
  tableParams: getTableListParams,
  onStatusChange: (arg: string) => void
) => {
  onStatusChange('Retrieving all table names');
  let allTables;
  try {
    allTables = (await getTableList(tableParams)) as Array<string>;
  } catch (e) {
    throw new Error('Failed loading table names');
  }

  if (!Array.isArray(allTables) || allTables.length === 0) {
    console.info('tableParams', tableParams);
    throw new Error('No tables found. Please verify DB name used.');
  }

  let tableMetadata = allTables;
  if (window.IS_VECTOR_DB_ENABLED) {
    tableMetadata = await getRelevantTableDetails(
      tableParams.databaseName,
      allTables,
      tableParams.executor
    );
  }

  onStatusChange('Filtering relevant tables');
  let relevantTables;
  try {
    relevantTables = await fetchFromLlm({
      url: TABLES_API_URL,
      data: {
        input: input,
        metadata: tableMetadata,
        database: tableParams.databaseName
      }
    });
  } catch (e) {
    throw new Error('Error filtering relevant tables.');
  }

  const tablesList = relevantTables?.tables;
  if (!Array.isArray(tablesList) || tablesList.length === 0) {
    throw new Error('Could not find any relevant tables.');
  }

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

const generateTableDDL = (tableObject: any, dialect: string): string => {
  const tableName = tableObject.name;

  const columnDefinitions = tableObject.columns
    .map((col: any) => {
      let columnDef = `${col.name} ${col.type}`;
      if (col.primaryKey) {
        columnDef += ' PRIMARY KEY';
      }
      if (col.foreignKey) {
        columnDef += ` FOREIGN KEY (${col.foreignKey.name}) REFERENCES ${col.foreignKey.to}`;
      }
      if (col.comment && col.comment != '') {
        columnDef += ` COMMENT '${col.comment}'`;
      }
      return columnDef;
    })
    .join(', ');

  // const partitions = tableObject.partitions.map((p: any) => `${p.name} ${p.type}`).join(', ');

  return `CREATE TABLE ${tableName} (${columnDefinitions});`;
};

const generateAllTableDDLs = (tableMetadatas: any[], dialect: string): string => {
  const allDDLs = tableMetadatas.map(table => generateTableDDL(table, dialect));
  return allDDLs.join('\n\n');
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
    try {
      const columns = await fetchColumnsData(databaseName, tableName, executor);
      const tableDetails = {
        dbName: databaseName,
        name: tableName,
        columns: columns.map(({ definition }) => {
          return definition;
        }),
        partitions: columns.partitions
      };
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
    if (e instanceof Error) {
      return handleError(e, e.message);
    }
  }

  // Generate DDL for tables
  const ddlString = generateAllTableDDLs(tableMetadata, dialect);

  onStatusChange('Optimizing SQL query');

  try {
    return await fetchFromLlm({
      url: SQL_API_URL,
      data: {
        task: 'optimize',
        sql: statement,
        dialect,
        metadata: {
          tables: tableMetadata,
          ddl: ddlString
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
  let tableMetadata;
  try {
    ({ tableMetadata } = await getTablesAndMetadata(nql, databaseName, executor, onStatusChange));
  } catch (e) {
    if (e instanceof Error) {
      return handleError(e, e.message);
    }
  }
  const ddlString = generateAllTableDDLs(tableMetadata, dialect);

  onStatusChange('Generating SQL query');
  try {
    return await fetchFromLlm({
      url: SQL_API_URL,
      data: {
        task: 'generate',
        input: nql,
        dialect,
        metadata: {
          tables: tableMetadata,
          ddl: ddlString
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
  let tableMetadata;
  try {
    ({ tableMetadata } = await getTablesAndMetadata(nql, databaseName, executor, onStatusChange));
  } catch (e) {
    if (e instanceof Error) {
      return handleError(e, e.message);
    }
  }
  const ddlString = generateAllTableDDLs(tableMetadata, dialect);

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
          tables: tableMetadata,
          ddl: ddlString
        }
      }
    });
  } catch (e) {
    return handleError(e, 'Call to AI to edit SQL query failed');
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
      if (e instanceof Error) {
        return handleError(e, e.message);
      }
    }
    const ddlString = generateAllTableDDLs(tableMetadata, dialect);
    onStatusChange('Generating explanation');
    return await fetchFromLlm({
      url: SQL_API_URL,
      data: {
        task: 'summarize',
        sql: statement,
        dialect,
        metadata: {
          tables: tableMetadata,
          ddl: ddlString
        }
      }
    });
  } catch (e) {
    return handleError(e, 'Call to AI to explain SQL query failed');
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
    if (e instanceof Error) {
      return handleError(e, e.message);
    }
  }
  const ddlString = generateAllTableDDLs(tableMetadata, dialect);
  onStatusChange('Generating corrected SQL query');
  try {
    return await fetchFromLlm({
      url: SQL_API_URL,
      data: {
        task: 'fix',
        sql: statement,
        dialect,
        metadata: {
          tables: tableMetadata,
          ddl: ddlString
        }
      }
    });
  } catch (e) {
    return handleError(e, 'Call to AI to fix SQL query failed');
  }
};
