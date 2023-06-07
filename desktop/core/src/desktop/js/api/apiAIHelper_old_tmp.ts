// import MD5 from 'crypto-js/MD5';
import { hueWindow } from 'types/types';

import Executor from '../apps/editor/execution/executor';
import dataCatalog from '../catalog/dataCatalog';
import { getRelevantTableDetails } from 'reactComponents/loadCatalogs';

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

const API_URL = '/api/editor/chat/';
const EXTRACT_CODE_AND_EXPLAIN_REGEX =
  /<code>([\s\S]*?)<\/code>[\s\S]*?<explain>([\s\S]*?)<\/explain>/;
const EXTRACT_CODE_AND_ASSUMPTIONS_REGEX =
  /<code>(.*?)<\/code>.*<assumptions>(.*?)<\/assumptions>/s;
const EXTRACT_TABLES = /<tables>(.*?)<\/tables>/;

const extractLlmResponse = (response: any) => {
  // TODO: Make this onfigurable for different LLMs
  return response.hasOwnProperty('open_ai') ? response.open_ai : '';
};

const extractCodeAndExplanation = (llmResponse: string) => {
  const matches = EXTRACT_CODE_AND_EXPLAIN_REGEX.exec(llmResponse) || [];
  return { sql: matches[1]?.trim(), explanation: matches[2].trim() };
};

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
  })
    .then(response => response.json())
    .then(extractLlmResponse);

  return promise;
};

const generateExplanation: GenerateExplanation = async ({ statement, dialect }) => {
  // TODO: handle exceptions
  const result = await fetchFromLlm({
    url: API_URL,
    data: {
      type: 'explain',
      dialect,
      prompt: statement
    }
  });

  console.info('explain result', JSON.stringify(result));
  return result;
};

const generateCorrectedSql: GenerateCorrectedSql = async ({
  statement,
  dialect,
  onStatusChange
}) => {
  // TODO: Add call onStatusChange if we include metadata in the LLM call
  const multiPartResponse = await fetchFromLlm({
    url: API_URL,
    data: {
      type: 'correctandexplain',
      prompt: statement,
      dialect
    }
  });

  try {
    return extractCodeAndExplanation(multiPartResponse);
  } catch {
    console.error(multiPartResponse);
    return {
      error: {
        message: 'Sorry, the response from the AI model could not be interpreted.'
      }
    };
  }
};

const generateOptimizedSql: GenerateOptimizedSql = async ({
  statement,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  const allTables = (await getTableList({ databaseName, executor })) as Array<string>;
  console.info('allTables', allTables);
  onStatusChange('Finding relevant tables');
  const relevantTablesInTags = await fetchFromLlm({
    url: API_URL,
    data: {
      type: 'listRelevantTables',
      prompt: statement,
      metadata: allTables.toString()
    }
  });

  console.info('relevantTablesInTags', relevantTablesInTags);
  onStatusChange('Extracting table meta data');
  const relevantTables = EXTRACT_TABLES.exec(relevantTablesInTags) || [];
  const tableMetadata = await getTableMetaData(relevantTables);  

  onStatusChange('Generating SQL query');
  const multiPartResponse = await fetchFromLlm({
    url: API_URL,
    data: {
      type: 'optimize',
      prompt: statement,
      dialect
    }
  });
  try {
    return extractCodeAndExplanation(multiPartResponse);
  } catch (e) {
    console.error(multiPartResponse);
    return {
      error: {
        message: 'Sorry, the response from the AI model could not be interpreted.'
      }
    };
  }
};

const generateSQLfromNQL: GenerateSQLfromNQL = async ({
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  const allTables = (await getTableList({ databaseName, executor })) as Array<string>;
  console.info('allTables', allTables);
  onStatusChange('Finding relevant tables');
  const relevantTablesInTags = await fetchFromLlm({
    url: API_URL,
    data: {
      type: 'listRelevantTables',
      prompt: nql,
      metadata: allTables.toString()
    }
  });
  console.info('relevantTablesInTags', relevantTablesInTags);
  onStatusChange('Extracting table meta data');
  const relevantTables = EXTRACT_TABLES.exec(relevantTablesInTags) || [];
  const tableMetadata = await getTableMetaData(relevantTables);
  onStatusChange('Generating SQL query');
  const data = {
    type: 'generateSql',
    prompt: nql,
    metadata: JSON.stringify(tableMetadata),
    dialect
  };
  console.info(data);
  const multiPartResult = await fetchFromLlm({
    url: API_URL,
    data
  });
  console.info('multiPartResult', multiPartResult);
  const match = EXTRACT_CODE_AND_ASSUMPTIONS_REGEX.exec(multiPartResult) || [];
  return { sql: match[1]?.trim(), assumptions: match[2]?.trim() };
};

const generateEditedSQLfromNQL: GenerateEditedSQLfromNQL = async ({
  sql,
  nql,
  databaseName,
  executor,
  dialect,
  onStatusChange
}) => {
  const allTables = (await getTableList({ databaseName, executor })) as Array<string>;
  onStatusChange('Finding relevant tables');
  const relevantTablesInTags = await fetchFromLlm({
    url: API_URL,
    data: {
      type: 'listRelevantTables',
      prompt: nql,
      metadata: allTables.toString()
    }
  });
  onStatusChange('Extracting table meta data');
  const relevantTables = EXTRACT_TABLES.exec(relevantTablesInTags) || [];
  const tableMetadata = await getTableMetaData(relevantTables);
  onStatusChange('Generating SQL query');
  const data = {
    type: 'editSql',
    prompt: `
    SQL: ${sql}
    REQUESTED CHANGE: ${nql}`,
    metadata: JSON.stringify(tableMetadata),
    dialect
  };
  console.info('DATA SENTS:', data);
  const multiPartResult = await fetchFromLlm({
    url: API_URL,
    data
  });
  // SOMETIMES THE RESPONSE (USING <code>...</code> and <assumptions> ... </assumptions>)
  // IS NOT FORMATTED AS EXPECTED FROM CHATGPT
  console.info('multiPartResult', multiPartResult);
  const match = EXTRACT_CODE_AND_ASSUMPTIONS_REGEX.exec(multiPartResult) || [];
  return { sql: match[1]?.trim(), assumptions: match[2]?.trim() };
};

interface getTableListParams {
  databaseName: string;
  executor: Executor;
}
const getTableList = async ({ databaseName, executor }: getTableListParams) => {
  // TODO: USe real data
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve(['website_visitors']);
    }, 3000);
  });
  // const dbEntry = await dataCatalog.getEntry({
  //   path: databaseName,
  //   connector: executor?.connector(),
  //   namespace: executor?.namespace(),
  //   compute: executor?.compute()
  // });
  // const dbChildren = await dbEntry.getChildren();
  // const tableNames = dbChildren.map(({ name }) => name);
  // return tableNames;
};

const getTableMetaData = async (tableNames: Array<string>) => {
  // MOCK
  // TODO: Implement this as a 2nd step of generting SQL from NQL
  // We divide it into 3 separate steps so that the UI can show status on progress.
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve({
        tableName: 'web_logs',
        columns: [
          {
            name: '_version_',
            type: 'bigint',
            comment: ''
          },
          {
            name: 'app',
            type: 'string',
            comment: ''
          },
          {
            name: 'bytes',
            type: 'int',
            comment: ''
          },
          {
            name: 'city',
            type: 'string',
            comment: ''
          },
          {
            name: 'client_ip',
            type: 'string',
            comment: ''
          },
          {
            name: 'code',
            type: 'smallint',
            comment: ''
          },
          {
            name: 'country_code',
            type: 'string',
            comment: ''
          },
          {
            name: 'country_code3',
            type: 'string',
            comment: ''
          },
          {
            name: 'country_name',
            type: 'string',
            comment: ''
          },
          {
            name: 'device_family',
            type: 'string',
            comment: ''
          },
          {
            name: 'extension',
            type: 'string',
            comment: ''
          },
          {
            name: 'latitude',
            type: 'float',
            comment: ''
          },
          {
            name: 'longitude',
            type: 'float',
            comment: ''
          },
          {
            name: 'method',
            type: 'string',
            comment: ''
          },
          {
            name: 'os_family',
            type: 'string',
            comment: ''
          },
          {
            name: 'os_major',
            type: 'string',
            comment: ''
          },
          {
            name: 'protocol',
            type: 'string',
            comment: ''
          },
          {
            name: 'record',
            type: 'string',
            comment: ''
          },
          {
            name: 'referer',
            type: 'string',
            comment: ''
          },
          {
            name: 'region_code',
            type: 'string',
            comment: ''
          },
          {
            name: 'request',
            type: 'string',
            comment: ''
          },
          {
            name: 'subapp',
            type: 'string',
            comment: ''
          },
          {
            name: 'time',
            type: 'string',
            comment: ''
          },
          {
            name: 'url',
            type: 'string',
            comment: ''
          },
          {
            name: 'user_agent',
            type: 'string',
            comment: ''
          },
          {
            name: 'user_agent_family',
            type: 'string',
            comment: ''
          },
          {
            name: 'user_agent_major',
            type: 'string',
            comment: ''
          },
          {
            name: 'id',
            type: 'string',
            comment: ''
          },
          {
            name: 'date',
            type: 'string',
            comment: ''
          }
        ]
      });
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
