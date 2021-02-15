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
  CACHEABLE_TTL?: { default?: number; optimizer?: number };
  CLOSE_SESSIONS?: { [dialect: string]: boolean };
  CUSTOM_DASHBOARD_URL?: string;
  ENABLE_PREDICT?: boolean;
  HAS_CATALOG?: boolean;
  HAS_CONNECTORS?: boolean;
  HAS_OPTIMIZER?: boolean;
  AUTOCOMPLETE_TIMEOUT?: number;
  ENABLE_SQL_SYNTAX_CHECK?: boolean;
  HUE_BASE_URL?: string;
  LOGGED_USERNAME?: string;
  OPTIMIZER_MODE?: string;
  SHOW_ADD_MORE_EDITORS?: boolean;
  USER_IS_ADMIN?: boolean;
  USER_IS_HUE_ADMIN?: boolean;
  USER_VIEW_EDIT_USER_ENABLED?: boolean;
  WEB_SOCKETS_ENABLED?: boolean;
  WS_CHANNEL?: string;
  hueDebug?: HueDebug;
  DISABLE_LOCAL_STORAGE?: boolean;
}
