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

import { HueDebug } from 'utils/hueDebug';

export interface GenericApiResponse {
  status: number;
  message?: string;
}

declare global {
  export interface Moment {
    utc: (val: unknown) => Moment;
    format: (format: string) => string;
  }

  const moment: Moment & ((val: unknown) => Moment);
}

export interface hueWindow {
  ENABLE_SQL_SYNTAX_CHECK?: boolean;
  LOGGED_USERNAME?: string;
  WEB_SOCKETS_ENABLED?: boolean;
  WS_CHANNEL?: string;
  hueDebug?: HueDebug;
}
