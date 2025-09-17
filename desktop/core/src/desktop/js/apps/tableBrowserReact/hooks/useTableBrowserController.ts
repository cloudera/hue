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

import { useCallback, useEffect, useMemo, useState } from 'react';
import changeURL from '../../../utils/url/changeURL';
import {
  buildTableBrowserPath,
  getTableBrowserBasePath,
  parseTableBrowserPath
} from '../utils/routing';
import type { TableBrowserRoute } from '../utils/routing';
import type { TabKey } from '../sharedComponents/Tabs';

export interface TableBrowserController {
  locationPath: string;
  basePath: string;
  route: TableBrowserRoute;
  activeTab: TabKey;
  onTabChange: (key: TabKey) => void;
  refreshFromLocation: () => void;
  navigateToSources: () => void;
  navigateToSource: (sourceType: string) => void;
  navigateToDatabase: (database: string) => void;
  navigateToTable: (database: string, table: string) => void;
  navigateToColumn: (database: string, table: string, column: string) => void;
  navigateToField: (database: string, table: string, column: string, fields: string[]) => void;
}

export function useTableBrowserController(): TableBrowserController {
  const [locationPath, setLocationPath] = useState<string>(window.location.pathname);

  // Keep pathname updated on browser navigation
  useEffect(() => {
    const onPopState = () => setLocationPath(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const basePath = useMemo(() => getTableBrowserBasePath(locationPath), [locationPath]);
  const route = useMemo(() => parseTableBrowserPath(locationPath), [locationPath]);

  const [activeTab, setActiveTab] = useState<TabKey>(() => {
    const params = new URLSearchParams(window.location.search);
    return ((params.get('tab') as TabKey) || 'overview') as TabKey;
  });

  // Sync activeTab when user navigates via browser (search may change)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = (params.get('tab') as TabKey) || 'overview';
    setActiveTab(tabParam);
  }, [route.sourceType, route.database, route.table]);

  const refreshFromLocation = useCallback(() => {
    setLocationPath(window.location.pathname);
    const params = new URLSearchParams(window.location.search);
    const tabParam = (params.get('tab') as TabKey) || 'overview';
    setActiveTab(tabParam);
  }, []);

  const onTabChange = useCallback((key: TabKey) => {
    const url = new URL(window.location.href);
    url.searchParams.set('tab', key);
    changeURL(url.pathname + url.search);
    setActiveTab(key);
  }, []);

  const navigateToSources = useCallback(() => {
    const newPath = buildTableBrowserPath(basePath);
    changeURL(newPath);
    setLocationPath(newPath);
  }, [basePath]);

  const navigateToSource = useCallback(
    (sourceType: string) => {
      const newPath = buildTableBrowserPath(basePath, sourceType);
      changeURL(newPath);
      setLocationPath(newPath);
    },
    [basePath]
  );

  const navigateToDatabase = useCallback(
    (database: string) => {
      const src = route.sourceType || 'hive';
      const newPath = buildTableBrowserPath(basePath, src, database);
      changeURL(newPath);
      setLocationPath(newPath);
    },
    [basePath, route.sourceType]
  );

  const navigateToTable = useCallback(
    (database: string, table: string) => {
      const src = route.sourceType || 'hive';
      const newPath = buildTableBrowserPath(basePath, src, database, table);
      changeURL(newPath);
      setLocationPath(newPath);
    },
    [basePath, route.sourceType]
  );

  const navigateToColumn = useCallback(
    (database: string, table: string, column: string) => {
      const src = route.sourceType || 'hive';
      const newPath = buildTableBrowserPath(basePath, src, database, table, column);
      changeURL(newPath);
      setLocationPath(newPath);
    },
    [basePath, route.sourceType]
  );

  const navigateToField = useCallback(
    (database: string, table: string, column: string, fields: string[]) => {
      const src = route.sourceType || 'hive';
      const newPath = buildTableBrowserPath(basePath, src, database, table, column, fields);
      changeURL(newPath);
      setLocationPath(newPath); // Manually update location path since changeURL doesn't trigger popstate
    },
    [basePath, route.sourceType]
  );

  return {
    locationPath,
    basePath,
    route,
    activeTab,
    onTabChange,
    refreshFromLocation,
    navigateToSources,
    navigateToSource,
    navigateToDatabase,
    navigateToTable,
    navigateToColumn,
    navigateToField
  };
}
