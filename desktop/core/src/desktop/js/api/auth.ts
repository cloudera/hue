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

import { get, post } from 'api/utils';

export enum AuthType {
  hue = 'hue',
  jwt = 'jwt'
}

const LOGOUT_URL = '/hue/accounts/logout';
const LOGIN_URL = '/hue/accounts/login';

const JWT_URL = 'iam/v1/get/auth-token/';

export const login = async (
  username: string,
  password: string,
  auth = AuthType.jwt
): Promise<void> => {
  if (auth === AuthType.jwt) {
    return post(JWT_URL, { username, password });
  }

  if (auth === AuthType.hue) {
    await get(LOGOUT_URL);
    const response = await get<string>(LOGIN_URL);
    const csrfMatch = response.match(/name='csrfmiddlewaretoken'\s+value='([^']+)'/);
    if (csrfMatch) {
      return post(LOGIN_URL, { username, password, csrfmiddlewaretoken: csrfMatch[1] });
    }
    throw new Error('No csrf middleware token found!');
  }
  throw new Error('Unknown auth method specified!');
};
