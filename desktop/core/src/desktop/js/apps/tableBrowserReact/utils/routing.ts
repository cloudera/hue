// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

export interface TableBrowserRoute {
  sourceType?: string;
  database?: string;
  table?: string;
  column?: string;
  fields?: string[];
}

export function parseTableBrowserPath(pathname: string): TableBrowserRoute {
  const idx = pathname.indexOf('/tablebrowser');
  if (idx === -1) {
    return {};
  }
  const rest = pathname.substring(idx + '/tablebrowser'.length);
  const segments = rest.split('/').filter(Boolean);
  const route = {
    sourceType: segments[0],
    database: segments[1],
    table: segments[2],
    column: segments[3]
  } as TableBrowserRoute;
  if (segments.length > 4) {
    route.fields = segments.slice(4);
  }
  return route;
}

export function buildTableBrowserPath(
  base: string,
  sourceType?: string,
  database?: string,
  table?: string,
  column?: string,
  fields?: string[]
): string {
  const parts = [
    base,
    '/tablebrowser',
    sourceType ? `/${encodeURIComponent(sourceType)}` : '',
    database ? `/${encodeURIComponent(database)}` : '',
    table ? `/${encodeURIComponent(table)}` : '',
    column ? `/${encodeURIComponent(column)}` : ''
  ];
  if (fields && fields.length) {
    fields.forEach(f => parts.push(`/${encodeURIComponent(f)}`));
  }
  return parts.join('');
}

export function getTableBrowserBasePath(pathname: string = window.location.pathname): string {
  const baseIdx = pathname.indexOf('/tablebrowser');
  return baseIdx !== -1 ? pathname.substring(0, baseIdx) : '';
}
