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

import { post } from 'api/utils';
import { AUTOCOMPLETE_API_PREFIX } from 'api/urls';
import { UdfArgument, UdfDetails } from 'sql/reference/types';
import { Connector } from 'config/types';
import I18n from 'utils/i18n';

export interface ApiUdf {
  name: string;
  is_builtin?: string;
  is_persistent?: string;
  return_type?: string;
  signature?: string;
  description?: string;
}

const FUNCTION_OPERATION = 'function';
const FUNCTIONS_OPERATION = 'functions';
const DEFAULT_DESCRIPTION = I18n('No description available.');
const DEFAULT_RETURN_TYPES = ['T'];
const DEFAULT_ARGUMENTS = [[{ type: 'T', multiple: true }]];

const SIGNATURE_REGEX = /([a-z]+(?:\.{3})?)/gi;
const TYPE_REGEX = /(?<type>[a-z]+)(?<multiple>\.{3})?/i;

const stripPrecision = (typeString: string): string => typeString.replace(/\(\*(,\*)?\)/g, '');

const adaptApiUdf = (apiUdf: ApiUdf): UdfDetails => {
  const signature = apiUdf.name + '()';
  return {
    name: apiUdf.name,
    returnTypes: extractReturnTypes(apiUdf),
    arguments: extractArgumentTypes(apiUdf),
    signature: signature,
    draggable: signature,
    description: DEFAULT_DESCRIPTION,
    described: false
  };
};

const extractReturnTypes = (apiUdf: ApiUdf): string[] =>
  apiUdf.return_type ? [stripPrecision(apiUdf.return_type)] : DEFAULT_RETURN_TYPES;

export const extractArgumentTypes = (apiUdf: ApiUdf): UdfArgument[][] => {
  if (apiUdf.signature) {
    const cleanSignature = stripPrecision(apiUdf.signature);
    if (cleanSignature === '()') {
      return [];
    }
    const match = cleanSignature.match(SIGNATURE_REGEX);
    if (match) {
      return match.map(argString => {
        const typeMatch = argString.match(TYPE_REGEX);
        if (typeMatch && typeMatch.groups) {
          const arg: UdfArgument = { type: typeMatch.groups.type };
          if (typeMatch.groups.multiple) {
            arg.multiple = true;
          }
          return [arg];
        } else {
          return [];
        }
      });
    }
  }
  return DEFAULT_ARGUMENTS;
};

export const mergeArgumentTypes = (target: UdfArgument[][], additional: UdfArgument[][]): void => {
  for (let i = 0; i < target.length; i++) {
    if (i >= additional.length) {
      break;
    }
    if (target[i][0].type === 'T') {
      continue;
    }
    if (additional[i][0].type === 'T') {
      target[i] = additional[i];
      continue;
    }
    target[i].push(...additional[i]);
  }
};

export const adaptApiFunctions = (functions: ApiUdf[]): UdfDetails[] => {
  const udfs: UdfDetails[] = [];
  const adapted: { [attr: string]: UdfDetails } = {};
  functions.forEach(apiUdf => {
    if (adapted[apiUdf.name]) {
      const adaptedUdf = adapted[apiUdf.name];

      const additionalArgs = extractArgumentTypes(apiUdf);
      mergeArgumentTypes(adaptedUdf.arguments, additionalArgs);

      if (adaptedUdf.returnTypes[0] !== 'T') {
        const additionalReturnTypes = extractReturnTypes(apiUdf);
        if (additionalReturnTypes[0] !== 'T') {
          adaptedUdf.returnTypes.push(...additionalReturnTypes);
        } else {
          adaptedUdf.returnTypes = additionalReturnTypes;
        }
      }

      // Make sure the return types are unique
      adaptedUdf.returnTypes = [...new Set(adaptedUdf.returnTypes)];
    } else {
      adapted[apiUdf.name] = adaptApiUdf(apiUdf);
      udfs.push(adapted[apiUdf.name]);
    }
  });
  return udfs;
};

const createUrl = (database?: string, udf?: UdfDetails): string => {
  if (database && udf) {
    return `${AUTOCOMPLETE_API_PREFIX}${database}/${udf.name}`;
  }
  if (database) {
    return `${AUTOCOMPLETE_API_PREFIX}${database}/`;
  }
  if (udf) {
    return `${AUTOCOMPLETE_API_PREFIX}${udf.name}`;
  }
  return AUTOCOMPLETE_API_PREFIX;
};

const createRequestData = (connector: Connector, operation: string) => ({
  notebook: {},
  snippet: JSON.stringify({
    type: connector.id
  }),
  operation: operation
});

export const fetchUdfs = async (
  connector: Connector,
  database?: string,
  silenceErrors = true
): Promise<UdfDetails[]> => {
  const url = createUrl(database);
  const data = createRequestData(connector, FUNCTIONS_OPERATION);

  try {
    const response = await post<{ functions?: ApiUdf[] }>(url, data, {
      silenceErrors: silenceErrors
    });
    if (response?.functions) {
      return adaptApiFunctions(response.functions);
    }
  } catch (err) {}
  return [];
};

export const fetchDescribe = async (
  connector: Connector,
  udf: UdfDetails,
  database?: string,
  silenceErrors = true
): Promise<ApiUdf | undefined> => {
  const url = createUrl(database, udf);
  const data = createRequestData(connector, FUNCTION_OPERATION);

  try {
    const response = await post<{ function?: ApiUdf }>(url, data, { silenceErrors: silenceErrors });
    if (response?.function) {
      return response.function;
    }
  } catch (err) {}
};
