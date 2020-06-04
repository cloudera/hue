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

import { simplePostAsync } from 'api/apiUtils';
import { AUTOCOMPLETE_API_PREFIX } from 'api/urls';
import I18n from 'utils/i18n';

const FUNCTIONS_OPERATION = 'functions';
const DEFAULT_DESCRIPTION = I18n('No description available.');
const DEFAULT_RETURN_TYPE = ['T'];
const DEFAULT_ARGUMENTS = [[{ type: 'T', multiple: true }]];

const SIGNATURE_REGEX = /([a-z]+(?:\.{3})?)/gi;
const TYPE_REGEX = /(?<type>[a-z]+)(?<multiple>\.{3})?/i;

const stripPrecision = typeString => typeString.replace(/\(\*(,\*)?\)/g, '');

// TODO: Extend with arguments etc reported by the API
export const adaptApiUdf = apiUdf => {
  const signature = apiUdf.name + '()';
  return {
    returnTypes: apiUdf.returnTypes || DEFAULT_RETURN_TYPE,
    arguments: apiUdf.arguments || DEFAULT_ARGUMENTS,
    signature: signature,
    draggable: signature,
    description: DEFAULT_DESCRIPTION
  };
};

export const extractArgumentTypes = apiUdf => {
  if (apiUdf.signature) {
    const cleanSignature = stripPrecision(apiUdf.signature);
    if (cleanSignature === '()') {
      return [];
    }
    const match = cleanSignature.match(SIGNATURE_REGEX);
    if (match) {
      return match.map(argString => {
        const typeMatch = argString.match(TYPE_REGEX);
        const arg = { type: typeMatch.groups.type };
        if (typeMatch.groups.multiple) {
          arg.multiple = true;
        }
        return [arg];
      });
    }
  }
  return DEFAULT_ARGUMENTS;
};

export const mergeArgumentTypes = (target, additional) => {
  for (let i = 0; i < target.length; i++) {
    if (i >= additional.length) {
      break;
    }
    if (target[i].type === 'T') {
      continue;
    }
    if (additional[i].type === 'T') {
      target[i] = additional[i];
      continue;
    }
    target[i].push(...additional[i]);
  }
};

export const adaptApiFunctions = functions => {
  const udfs = [];
  const adapted = {};
  functions.forEach(apiUdf => {
    apiUdf.arguments = extractArgumentTypes(apiUdf);
    apiUdf.returnTypes = apiUdf.return_type ? [stripPrecision(apiUdf.return_type)] : ['T'];
    if (adapted[apiUdf.name]) {
      const adaptedUdf = adapted[apiUdf.name];
      mergeArgumentTypes(adaptedUdf.arguments, apiUdf.arguments);
      if (adaptedUdf.returnTypes[0] !== 'T') {
        if (apiUdf.returnTypes[0] === 'T') {
          adaptedUdf.returnTypes = ['T'];
        } else if (adaptedUdf.returnTypes[0] !== apiUdf.returnTypes[0]) {
          adaptedUdf.returnTypes.push(...apiUdf.returnTypes);
        }
      }
    } else {
      adapted[apiUdf.name] = apiUdf;
      udfs.push(apiUdf);
    }
  });
  return udfs;
};

/**
 * @param {Object} options
 * @param {Connector} options.connector
 * @param {string} [options.database]
 * @param {boolean} [options.silenceErrors]
 *
 * @return {Promise}
 */
export const fetchUdfs = async options => {
  let url = AUTOCOMPLETE_API_PREFIX;
  if (options.database) {
    url += '/' + options.database;
  }

  const data = {
    notebook: {},
    snippet: JSON.stringify({
      type: options.connector.id
    }),
    operation: FUNCTIONS_OPERATION
  };

  try {
    const response = await simplePostAsync(url, data, options);

    if (response && response.functions) {
      return adaptApiFunctions(response.functions);
    }
    return (response && response.functions) || [];
  } catch (err) {
    return [];
  }
};
