import huePubSub from 'utils/huePubSub';

const fetchColumnsData = async (databaseName, tableName, executor) => {
  const dbEntry = await executor.dataCatalog.getEntry({
    path: [databaseName, tableName],
    connector: executor.connector,
    namespace: executor.namespace,
    compute: executor.compute
  });
  const columns = await dbEntry.getChildren();
  return columns;
};

export const getRelevantTableDetails = async (databaseName, tableNames, executor) => {
  const relevantTables = [];
  for (const tableName of tableNames) {
    const columns = await fetchColumnsData(databaseName, tableName, executor);
    const tableDetails = {
      tableName: tableName,
      columns: columns.map(({ definition }) => definition)
    };
    relevantTables.push(tableDetails);
  }
  return relevantTables;
};

const delay = duration => new Promise(resolve => setTimeout(resolve, duration));

const getCacheProgress = databaseName => {
  const progressKey = 'database_cache_progress_' + databaseName;
  const progress = localStorage.getItem(progressKey);
  return progress ? parseInt(progress, 10) : 0;
};

export async function LoadDataCatalogs() {
  huePubSub.subscribe('fetch_tables_metadata', async data => {
    const dataCatalogEntry = await data.sourceMetaPromise;
    if (!dataCatalogEntry.tables_meta) {
      return;
    }

    const databaseName = data.entry.path[0];
    const totalTables = dataCatalogEntry.tables_meta.length;
    let completedTables = 0;

    for (const eachTable of dataCatalogEntry.tables_meta) {
      await delay(100);
      await fetchColumnsData(databaseName, eachTable.name, data.entry);
      completedTables++;
      const progress = Math.floor((completedTables / totalTables) * 100);
      localStorage.setItem('database_cache_progress_' + databaseName, progress);
    }
  });
}
