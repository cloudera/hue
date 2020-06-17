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

import { SetOptions, UdfArgument, UdfCategory, UdfCategoryFunctions, UdfDetails} from 'sql/reference/types';
import { Connector } from 'types';
import { matchesType } from './typeUtils';
import I18n from 'utils/i18n';
import huePubSub from 'utils/huePubSub';
import { clearUdfCache, getCachedUdfCategories, setCachedUdfCategories } from './apiCache';
import { fetchUdfs } from './apiUtils';

export const CLEAR_UDF_CACHE_EVENT = 'hue.clear.udf.cache';

const SET_REFS: { [attr: string]: () => Promise<{ SET_OPTIONS?: SetOptions }> } = {
  // @ts-ignore
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/setReference')
};

const UDF_REFS: { [attr: string]: () => Promise<{ UDF_CATEGORIES?: UdfCategory[] }> } = {
  // @ts-ignore
  generic: async () => import(/* webpackChunkName: "generic-ref" */ './generic/udfReference'),
  // @ts-ignore
  hive: async () => import(/* webpackChunkName: "hive-ref" */ './hive/udfReference'),
  // @ts-ignore
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/udfReference'),
  // @ts-ignore
  pig: async () => import(/* webpackChunkName: "pig-ref" */ './pig/udfReference')
};

const IGNORED_UDF_REGEX = /^[!=$%&*+-/<>^|~]+$/;

const mergedUdfPromises: { [attr: string]: Promise<UdfCategory[]> } = {};

const getMergedUdfKey = (connector: Connector, database?: string): string => {
  let key = connector.id;
  if (database) {
    key += '_' + database;
  }
  return key;
};

export const hasUdfCategories = (connector: Connector): boolean =>
  typeof UDF_REFS[connector.dialect] !== 'undefined';

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
    // TODO: Impala reports the same UDF multiple times, once per argument type.
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
  const apiUdfs = await fetchUdfs({
    connector: connector,
    database: database,
    silenceErrors: true
  });

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
  connector: Connector,
  database?: string
): Promise<UdfCategory[]> => {
  const promiseKey = getMergedUdfKey(connector, database);
  if (!mergedUdfPromises[promiseKey]) {
    mergedUdfPromises[promiseKey] = new Promise(async resolve => {
      const cachedCategories = await getCachedUdfCategories(connector, database);
      if (cachedCategories) {
        return cachedCategories;
      }
      let categories: UdfCategory[] = [];
      if (UDF_REFS[connector.dialect]) {
        const module = await UDF_REFS[connector.dialect]();
        if (module.UDF_CATEGORIES) {
          categories = module.UDF_CATEGORIES;
        }
      }
      await mergeWithApiUdfs(categories, connector, database);
      await setCachedUdfCategories(connector, database, categories);
      resolve(categories);
    });
  }

  return await mergedUdfPromises[promiseKey];
};

export const findUdf = async (
  connector: Connector,
  functionName: string
): Promise<UdfDetails[]> => {
  const categories = await getUdfCategories(connector);
  const found: UdfDetails[] = [];
  categories.forEach(category => {
    if (category.functions[functionName]) {
      found.push(category.functions[functionName]);
    }
  });
  return found;
};

export const getReturnTypesForUdf = async (
  connector: Connector,
  functionName: string
): Promise<string[]> => {
  if (!functionName) {
    return ['T'];
  }
  const udfs = await findUdf(connector, functionName);
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
  connector: Connector,
  returnTypes: string[],
  includeAggregate?: boolean,
  includeAnalytic?: boolean
): Promise<UdfDetails[]> => {
  const categories = await getUdfCategories(connector);
  const result: UdfDetails[] = [];
  categories.forEach(category => {
    if (
      (!category.isAnalytic && !category.isAggregate) ||
      (includeAggregate && category.isAggregate) ||
      (includeAnalytic && category.isAnalytic)
    ) {
      Object.keys(category.functions).forEach(udfName => {
        const udf = category.functions[udfName];
        if (!returnTypes || matchesType(connector.dialect, returnTypes, udf.returnTypes)) {
          result.push(udf);
        }
      });
    }
  });
  result.sort((a, b) => a.name.localeCompare(b.name));
  return result;
};

export const getArgumentDetailsForUdf = async (
  connector: Connector,
  functionName: string,
  argumentPosition: number
): Promise<UdfArgument[]> => {
  const foundFunctions = await findUdf(connector, functionName);
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

export const getSetOptions = async (connector: Connector): Promise<SetOptions> => {
  if (SET_REFS[connector.dialect]) {
    const module = await SET_REFS[connector.dialect]();
    if (module.SET_OPTIONS) {
      return module.SET_OPTIONS;
    }
  }
  return {};
};

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
