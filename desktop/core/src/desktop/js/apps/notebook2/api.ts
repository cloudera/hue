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

import axios from 'axios';

type FormatSqlApiResponse = {
  formatted_statements?: string;
  status: number;
};

const FORMAT_SQL_API_URL = '/notebook/api/format';

export const formatSql = async (options: {
  statements: string;
  silenceErrors?: boolean;
}): Promise<string> => {
  try {
    const params = new URLSearchParams();
    params.append('statements', options.statements);
    const response = await axios.post<FormatSqlApiResponse>(FORMAT_SQL_API_URL, params);

    if (response.data.status !== -1 && response.data.formatted_statements) {
      return response.data.formatted_statements;
    }
  } catch (err) {
    if (!options.silenceErrors) {
      throw err;
    }
  }
  return options.statements;
};
