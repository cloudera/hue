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

import {
  SqlReferenceProvider,
  UdfArgument,
  UdfCategory,
  UdfCategoryFunctions,
  UdfDetails
} from 'sql/reference/types';
import { Connector } from 'config/types';
import { matchesType } from './typeUtils';
import I18n from 'utils/i18n';
import huePubSub from 'utils/huePubSub';
import { clearUdfCache, getCachedUdfCategories, setCachedUdfCategories } from './apiCache';
import { fetchDescribe, fetchUdfs } from './apiUtils';

export const CLEAR_UDF_CACHE_EVENT = 'hue.clear.udf.cache';
export const DESCRIBE_UDF_EVENT = 'hue.describe.udf';
export const UDF_DESCRIBED_EVENT = 'hue.udf.described';

const IGNORED_UDF_REGEX = /^[!=$%&*+-/<>^|~]+$/;

const mergedUdfPromises: { [attr: string]: Promise<UdfCategory[]> } = {};

const getMergedUdfKey = (connector: Connector, database?: string): string => {
  let key = connector.id;
  if (database) {
    key += '_' + database;
  }
  return key;
};

const findUdfsToAdd = (
  apiUdfs: UdfDetails[],
  existingCategories: UdfCategory[]
): UdfCategoryFunctions => {
  const existingUdfNames = new Set();
  existingCategories.forEach(category => {
    Object.keys(category.functions).forEach(udfName => {
      existingUdfNames.add(udfName.toUpperCase());
    });
  });

  const result: UdfCategoryFunctions = {};

  apiUdfs.forEach(apiUdf => {
    if (
      !result[apiUdf.name] &&
      !existingUdfNames.has(apiUdf.name.toUpperCase()) &&
      !IGNORED_UDF_REGEX.test(apiUdf.name)
    ) {
      result[apiUdf.name] = apiUdf;
    }
  });

  return result;
};

const mergeWithApiUdfs = async (
  categories: UdfCategory[],
  connector: Connector,
  database?: string
) => {
  const apiUdfs = await fetchUdfs(connector, database);

  if (apiUdfs.length) {
    const additionalUdfs = findUdfsToAdd(apiUdfs, categories);
    if (Object.keys(additionalUdfs).length) {
      const generalCategory = {
        name: I18n('General'),
        functions: additionalUdfs
      };
      categories.unshift(generalCategory);
    }
  }
};

export const getUdfCategories = async (
  sqlReferenceProvider: SqlReferenceProvider,
  connector: Connector,
  database?: string
): Promise<UdfCategory[]> => {
  const promiseKey = getMergedUdfKey(connector, database);
  if (!mergedUdfPromises[promiseKey]) {
    mergedUdfPromises[promiseKey] = new Promise(async resolve => {
      const cachedCategories = await getCachedUdfCategories(connector, database);
      if (cachedCategories) {
        resolve(cachedCategories);
      }
      let categories: UdfCategory[] = [];
      if (connector.dialect && sqlReferenceProvider.hasUdfCategories(connector.dialect)) {
        categories = await sqlReferenceProvider.getUdfCategories(connector.dialect);
        categories.forEach(category => {
          Object.values(category.functions).forEach(udf => {
            udf.described = true;
          });
        });
      }
      await mergeWithApiUdfs(categories, connector, database);
      await setCachedUdfCategories(connector, database, categories);
      resolve(categories);
    });
  }

  return await mergedUdfPromises[promiseKey];
};

export const findUdf = async (
  sqlReferenceProvider: SqlReferenceProvider,
  connector: Connector,
  functionName: string
): Promise<UdfDetails[]> => {
  const categories = await getUdfCategories(sqlReferenceProvider, connector);
  const found: UdfDetails[] = [];
  categories.forEach(category => {
    if (category.functions[functionName]) {
      found.push(category.functions[functionName]);
    }
  });
  return found;
};

export const getReturnTypesForUdf = async (
  sqlReferenceProvider: SqlReferenceProvider,
  connector: Connector,
  functionName: string
): Promise<string[]> => {
  if (!functionName) {
    return ['T'];
  }
  const udfs = await findUdf(sqlReferenceProvider, connector, functionName);
  if (!udfs.length) {
    let returnTypesPresent = false;
    const returnTypes = new Set<string>();
    udfs.forEach(udf => {
      if (udf.returnTypes) {
        returnTypesPresent = true;
        udf.returnTypes.forEach(type => returnTypes.add(type));
      }
    });
    if (returnTypesPresent) {
      return [...returnTypes];
    }
  }

  return ['T'];
};

export const getUdfsWithReturnTypes = async (
  sqlReferenceProvider: SqlReferenceProvider,
  connector: Connector,
  returnTypes: string[],
  includeAggregate?: boolean,
  includeAnalytic?: boolean
): Promise<UdfDetails[]> => {
  const categories = await getUdfCategories(sqlReferenceProvider, connector);
  const result: UdfDetails[] = [];
  categories.forEach(category => {
    if (
      (!category.isAnalytic && !category.isAggregate) ||
      (includeAggregate && category.isAggregate) ||
      (includeAnalytic && category.isAnalytic)
    ) {
      Object.keys(category.functions).forEach(udfName => {
        const udf = category.functions[udfName];
        if (
          !returnTypes ||
          (connector.dialect && matchesType(connector.dialect, returnTypes, udf.returnTypes))
        ) {
          result.push(udf);
        }
      });
    }
  });
  result.sort((a, b) => a.name.localeCompare(b.name));
  return result;
};

export const getArgumentDetailsForUdf = async (
  sqlReferenceProvider: SqlReferenceProvider,
  connector: Connector,
  functionName: string,
  argumentPosition: number
): Promise<UdfArgument[]> => {
  const foundFunctions = await findUdf(sqlReferenceProvider, connector, functionName);
  if (!foundFunctions.length) {
    return [{ type: 'T' }];
  }

  const possibleArguments: UdfArgument[] = [];
  foundFunctions.forEach(foundFunction => {
    const args = foundFunction.arguments;
    if (argumentPosition > args.length) {
      possibleArguments.push(...args[args.length - 1].filter(type => type.multiple));
    } else {
      possibleArguments.push(...args[argumentPosition - 1]);
    }
  });
  return possibleArguments;
};

const findUdfInCategories = (
  categories: UdfCategory[],
  udfName: string
): UdfDetails | undefined => {
  let foundUdf = undefined;
  categories.some(category =>
    Object.values(category.functions).some(udf => {
      if (udf.name === udfName) {
        foundUdf = udf;
        return true;
      }
    })
  );
  return foundUdf;
};

huePubSub.subscribe(
  DESCRIBE_UDF_EVENT,
  async (details: {
    sqlReferenceProvider: SqlReferenceProvider;
    connector: Connector;
    udfName: string;
    database?: string;
  }): Promise<void> => {
    const categories = await getUdfCategories(
      details.sqlReferenceProvider,
      details.connector,
      details.database
    );
    const foundUdf = findUdfInCategories(categories, details.udfName);
    if (foundUdf && !foundUdf.described) {
      const apiUdf = await fetchDescribe(details.connector, foundUdf, details.database);
      if (apiUdf) {
        if (apiUdf.description) {
          foundUdf.description = apiUdf.description;
        }
        if (apiUdf.signature) {
          foundUdf.signature = apiUdf.signature;
        }
        foundUdf.described = true;
        await setCachedUdfCategories(details.connector, details.database, categories);
        huePubSub.publish(UDF_DESCRIBED_EVENT, {
          connector: details.connector,
          database: details.database,
          udf: foundUdf
        });
      }
    }
  }
);

huePubSub.subscribe(
  CLEAR_UDF_CACHE_EVENT,
  async (details: { connector: Connector; callback: () => void }) => {
    await clearUdfCache(details.connector);
    Object.keys(mergedUdfPromises).forEach(key => {
      if (key === details.connector.id || key.indexOf(details.connector.id + '_') === 0) {
        delete mergedUdfPromises[key];
      }
    });
    if (details.callback) {
      details.callback();
    }
  }
);
