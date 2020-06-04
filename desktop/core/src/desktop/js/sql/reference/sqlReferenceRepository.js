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

import ApiHelper from 'api/apiHelper';
import { matchesType } from './typeUtils';
import I18n from 'utils/i18n';
import huePubSub from 'utils/huePubSub';
import { clearUdfCache, getCachedApiUdfs, setCachedApiUdfs } from './sqlReferenceRepositoryCache';

export const CLEAR_UDF_CACHE_EVENT = 'hue.clear.udf.cache';

const SET_REFS = {
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/setReference')
};

const UDF_REFS = {
  generic: async () => import(/* webpackChunkName: "generic-ref" */ './generic/udfReference'),
  hive: async () => import(/* webpackChunkName: "hive-ref" */ './hive/udfReference'),
  impala: async () => import(/* webpackChunkName: "impala-ref" */ './impala/udfReference'),
  pig: async () => import(/* webpackChunkName: "pig-ref" */ './pig/udfReference')
};

const DEFAULT_DESCRIPTION = I18n('No description available.');
const DEFAULT_RETURN_TYPE = ['T'];
const DEFAULT_ARGUMENTS = [[{ type: 'T', multiple: true }]];
const IGNORED_UDF_REGEX = /^[!=$%&*+-/<>^|~]+$/;

const mergedUdfPromises = {};

const getMergedUdfKey = (connector, database) => {
  let key = connector.id;
  if (database) {
    key += '_' + database;
  }
  return key;
};

export const hasUdfCategories = connector => typeof UDF_REFS[connector.dialect] !== 'undefined';

// TODO: Extend with arguments etc reported by the API
const adaptApiUdf = apiUdf => {
  const signature = apiUdf.name + '()';
  return {
    returnTypes: DEFAULT_RETURN_TYPE,
    arguments: DEFAULT_ARGUMENTS,
    signature: signature,
    draggable: signature,
    description: DEFAULT_DESCRIPTION
  };
};

const findUdfsToAdd = (apiUdfs, existingCategories) => {
  const existingUdfNames = new Set();
  existingCategories.forEach(category => {
    Object.keys(category.functions).forEach(udfName => {
      existingUdfNames.add(udfName.toUpperCase());
    });
  });

  const result = {};

  apiUdfs.forEach(apiUdf => {
    // TODO: Impala reports the same UDF multiple times, once per argument type.
    if (
      !result[apiUdf.name] &&
      !existingUdfNames.has(apiUdf.name.toUpperCase()) &&
      !IGNORED_UDF_REGEX.test(apiUdf.name)
    ) {
      result[apiUdf.name] = adaptApiUdf(apiUdf);
    }
  });

  return result;
};

const mergeWithApiUdfs = async (categories, connector, database) => {
  let apiUdfs = await getCachedApiUdfs(connector, database);
  if (!apiUdfs) {
    apiUdfs = await ApiHelper.fetchUdfs({
      connector: connector,
      database: database,
      silenceErrors: true
    });
    await setCachedApiUdfs(connector, database, apiUdfs);
  }

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

export const getUdfCategories = async (connector, database) => {
  const promiseKey = getMergedUdfKey(connector, database);
  if (!mergedUdfPromises[promiseKey]) {
    mergedUdfPromises[promiseKey] = new Promise(async resolve => {
      let categories = [];
      if (UDF_REFS[connector.dialect]) {
        const module = await UDF_REFS[connector.dialect]();
        if (module.UDF_CATEGORIES) {
          categories = module.UDF_CATEGORIES;
        }
      }
      await mergeWithApiUdfs(categories, connector, database);

      resolve(categories);
    });
  }

  return await mergedUdfPromises[promiseKey];
};

export const findUdf = async (connector, functionName) => {
  const categories = await getUdfCategories(connector);
  let found = undefined;
  categories.some(category => {
    if (category.functions[functionName]) {
      found = category.functions[functionName];
      return true;
    }
  });
  return found;
};

export const getReturnTypesForUdf = async (connector, functionName) => {
  if (!functionName) {
    return ['T'];
  }
  const udf = await findUdf(connector, functionName);
  if (!udf || !udf.returnTypes) {
    return ['T'];
  }
  return udf.returnTypes;
};

export const getUdfsWithReturnTypes = async (
  connector,
  returnTypes,
  includeAggregate,
  includeAnalytic
) => {
  const categories = await getUdfCategories(connector);
  const result = {};
  categories.forEach(category => {
    if (
      (!category.isAnalytic && !category.isAggregate) ||
      (includeAggregate && category.isAggregate) ||
      (includeAnalytic && category.isAnalytic)
    ) {
      Object.keys(category.functions).forEach(udfName => {
        const udf = category.functions[udfName];
        if (!returnTypes || matchesType(connector, returnTypes, udf.returnTypes)) {
          result[udfName] = udf;
        }
      });
    }
  });
  return result;
};

export const getArgumentTypesForUdf = async (connector, functionName, argumentPosition) => {
  const foundFunction = await findUdf(connector, functionName);
  if (!foundFunction) {
    return ['T'];
  }
  const args = foundFunction.arguments;
  if (argumentPosition > args.length) {
    const multiples = args[args.length - 1].filter(type => {
      return type.multiple;
    });
    if (multiples.length > 0) {
      return multiples
        .map(argument => {
          return argument.type;
        })
        .sort();
    }
    return [];
  }
  return args[argumentPosition - 1]
    .map(argument => {
      return argument.type;
    })
    .sort();
};

export const getSetOptions = async connector => {
  if (SET_REFS[connector.dialect]) {
    const module = await SET_REFS[connector.dialect]();
    if (module.SET_OPTIONS) {
      return module.SET_OPTIONS;
    }
  }
  return {};
};

huePubSub.subscribe(CLEAR_UDF_CACHE_EVENT, async details => {
  await clearUdfCache(details.connector);
  Object.keys(mergedUdfPromises).forEach(key => {
    if (key === details.connector.id || key.indexOf(details.connector.id + '_') === 0) {
      delete mergedUdfPromises[key];
    }
  });
  if (details.callback) {
    details.callback();
  }
});
