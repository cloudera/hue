
import { getLastKnownConfig } from 'config/hueConfig';
import huePubSub from 'utils/huePubSub';
import sleep from 'utils/timing/sleep';


const fetchColumnsData = async (databaseName: string, tableName: string, executor: any) => {
  const dbEntry = await executor.dataCatalog.getEntry({
    path: [databaseName, tableName],
    connector: executor.connector,
    namespace: executor.namespace,
    compute: executor.compute
  });
  const columns = await dbEntry.getChildren();
  return columns;
};

export const getRelevantTableDetails = async (databaseName: string, tableNames: string[], executor: any) => {
  const relevantTables: any[] = [];
  for (const tableName of tableNames) {
    const columns = await fetchColumnsData(databaseName, tableName, executor);
    const tableDetails = {
      tableName: tableName,
      columns: columns.map(({ definition }: any) => definition),
      partitions: columns.partitions
    };
    relevantTables.push(tableDetails);
  }
  return relevantTables;
};

const getCacheProgress = (databaseName: string) => {
  const progressKey = 'database_cache_progress_' + databaseName;
  const progress = localStorage.getItem(progressKey);
  return progress ? parseInt(progress, 10) : 0;
};

export async function loadDataCatalogs() {
  const config = getLastKnownConfig();
  if (!(config?.hue_config?.is_ai_interface_enabled)) {
    return;
  }

  huePubSub.subscribe('fetch_tables_metadata', async (data: { sourceMetaPromise: Promise<any>; entry: any }) => {
    const dataCatalogEntry = await data.sourceMetaPromise;
    if (!dataCatalogEntry.tables_meta) {
      return;
    }

    const databaseName = data.entry.path[0];
    const totalTables = dataCatalogEntry.tables_meta.length;

    const config = getLastKnownConfig();
    const configLimit = config?.hue_config?.auto_fetch_table_meta_limit
    if (configLimit === 0) {
      return;
    }

    const numTablesToLoad = configLimit === -1 ? totalTables : Math.min(configLimit || 20, totalTables);

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
  });
}
