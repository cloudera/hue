// import MD5 from 'crypto-js/MD5';
import { hueWindow } from 'types/types';

import Executor from '../apps/editor/execution/executor';
import dataCatalog from '../catalog/dataCatalog';

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

const TABLES_API_URL = '/api/editor/ai/tables';
const SQL_API_URL = '/api/editor/ai/sql';

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

const generateExplanation: GenerateExplanation = async ({ statement, dialect }) => {
  // TODO: handle exceptions
  const response = await fetchFromLlm({
    url: SQL_API_URL,
    data: {
      task: 'summarize',
      sql: statement,
      dialect
    }
  });
  return response.summary;
};

const generateCorrectedSql: GenerateCorrectedSql = async ({
  statement,
  dialect,
  onStatusChange
}) => {
  // TODO: Add call onStatusChange if we include metadata in the LLM call
  return await fetchFromLlm({
    url: SQL_API_URL,
    data: {
      task: 'fix',
      sql: statement,
      dialect
    }
  });
};

const getRelevantTables = async (input: string, tableParams: getTableListParams, onStatusChange: (arg: string) => void) => {
  const allTables = (await getTableList(tableParams)) as Array<string>;
  console.info('allTables', allTables);
  onStatusChange('Finding relevant tables');

  const relevantTables = await fetchFromLlm({
    url: TABLES_API_URL,
    data: {
      input: input,
      metadata: allTables
    }
  });

  return relevantTables;
};

const generateOptimizedSql: GenerateOptimizedSql = async ({
  statement,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  const relevantTables = await getRelevantTables(
    statement,
    { databaseName, executor },
    onStatusChange
  );
  console.info('relevantTables', relevantTables);
  const tableMetadata = await getRelevantTableDetails(
    databaseName,
    relevantTables['tables'],
    executor
  );

  onStatusChange('Generating SQL query');
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
  executor: Executor
) => {
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


const generateSQLfromNQL: GenerateSQLfromNQL = async ({
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  const relevantTables = await getRelevantTables(nql, { databaseName, executor }, onStatusChange);
  const tableMetadata = await getRelevantTableDetails(
    databaseName,
    relevantTables['tables'],
    executor
  );

  onStatusChange('Generating SQL query');
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
};

const generateEditedSQLfromNQL: GenerateEditedSQLfromNQL = async ({
  sql,
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  const relevantTables = await getRelevantTables(nql, { databaseName, executor }, onStatusChange);
  console.info('relevantTables', relevantTables);
  const tableMetadata = await getRelevantTableDetails(
    databaseName,
    relevantTables['tables'],
    executor
  );


  onStatusChange('Generating SQL query');
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

const getTableMetaData = async (tableNames: Array<string>) => {
  // MOCK
  // TODO: Implement this as a 2nd step of generting SQL from NQL
  // We divide it into 3 separate steps so that the UI can show status on progress.
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve([
        {
          name: 'offices',
          columns: [
            {
              name: 'id',
              type: 'string',
              comment: ''
            },
            {
              name: 'address',
              type: 'string',
              comment: ''
            }
          ]
        }
      ]);
    }, 3000);
  });
};

// const oneDayMs = 1000 * 60 * 60 * 24;
// const cacheStore = {};
// export const fetchWithMemoryCache = async ({
//   url,
//   data,
//   method = 'POST',
//   contentType = 'application/json',
//   cacheName = 'shared',
//   keepFor = oneDayMs
// }) => {
//   if (!cacheStore[cacheName]) {
//     cacheStore[cacheName] = {};
//   }

//   const dataCacheKeyInput = method === 'POST' ? JSON.stringify(data) : '';
//   const cacheKey = MD5(`${url}${dataCacheKeyInput}`).toString();
//   const myStore = cacheStore[cacheName];
//   const cached = myStore[cacheKey];
//   if (cached) {
//     const { responseData, timestamp } = cached;
//     const expirationTime = new Date(timestamp).getTime() + keepFor;
//     if (expirationTime > Date.now()) {
//       return responseData;
//     }
//     delete myStore[cacheKey];
//   }

//   const promise = fetch(url, {
//     method,
//     headers: {
//       'Content-Type': contentType,
//       'X-Csrftoken': window.CSRF_TOKEN
//     },
//     body: JSON.stringify(data)
//   })
//     .then(response => response.json())
//     .then(responseData => {
//       const cacheItem = { responseData, timestamp: new Date() };
//       myStore[cacheKey] = cacheItem;
//       const cacheKeys = Object.keys(myStore);
//       if (cacheKeys.length > 50) {
//         delete myStore[cacheKeys[0]];
//       }
//       return responseData;
//     });

//   myStore[cacheKey] = { promise };
//   return promise;
// };
