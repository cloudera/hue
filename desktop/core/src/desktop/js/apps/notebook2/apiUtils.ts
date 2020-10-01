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

import { simplePost } from 'api/apiUtilsV2';
import { FORMAT_SQL_API } from 'api/urls';

export const formatSql = async (options: {
  statements: string;
  silenceErrors?: boolean;
}): Promise<string> => {
  try {
    const response = await simplePost<
      {
        formatted_statements: string;
        status: number;
      },
      { statements: string }
    >(FORMAT_SQL_API, options, {
      silenceErrors: !!options.silenceErrors,
      ignoreSuccessErrors: true
    });
    return (response && response.formatted_statements) || options.statements;
  } catch (err) {
    if (!options.silenceErrors) {
      throw err;
    }
  }
  return options.statements;
};
