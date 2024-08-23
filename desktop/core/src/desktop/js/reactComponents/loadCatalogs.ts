/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import { getLastKnownConfig } from 'config/hueConfig';
import huePubSub from 'utils/huePubSub';
import sleep from 'utils/timing/sleep';
import DataCatalogEntry, { DatabaseSourceMeta, SourceMeta } from 'catalog/DataCatalogEntry';

const fetchColumnsData = async (
  databaseName: string,
  tableName: string,
  entry: DataCatalogEntry
): Promise<DataCatalogEntry[]> => {
  const dbEntry = await entry.dataCatalog.getEntry({
    path: [databaseName, tableName],
    namespace: entry.namespace,
    compute: entry.compute
  });
  const columns = await dbEntry.getChildren();
  return columns;
};

export async function loadDataCatalogs(): Promise<void> {
  const config = getLastKnownConfig();
  if (!config?.hue_config?.is_ai_interface_enabled) {
    return;
  }

  huePubSub.subscribe(
    'fetch_tables_metadata',
    async (data: { sourceMetaPromise: Promise<SourceMeta>; entry: DataCatalogEntry }) => {
      const dataCatalogEntry = (await data.sourceMetaPromise) as DatabaseSourceMeta;
      if (!dataCatalogEntry.tables_meta) {
        return;
      }

      const databaseName = data.entry.path[0];
      const totalTables = dataCatalogEntry.tables_meta.length;

      const config = getLastKnownConfig();
      const configLimit = config?.hue_config?.auto_fetch_table_meta_limit;
      if (configLimit === 0) {
        return;
      }

      const numTablesToLoad =
        configLimit === -1 ? totalTables : Math.min(configLimit || 20, totalTables);

      let completedTables = 0;

      for (let i = 0; i < numTablesToLoad; i++) {
        const eachTable = dataCatalogEntry.tables_meta[i];
        await sleep(100);
        try {
          await fetchColumnsData(databaseName, eachTable.name, data.entry);
          completedTables++;
        } catch (error) {
          console.error('Error loading table: ' + eachTable.name, error);
          continue;
        }
        const progress = Math.floor((completedTables / numTablesToLoad) * 100);
        localStorage.setItem('database_cache_progress_' + databaseName, progress.toString());
      }
    }
  );
}
