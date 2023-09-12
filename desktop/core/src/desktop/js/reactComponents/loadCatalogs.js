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
      columns: columns.map(({ definition }) => definition),
      partitions: columns.partitions,
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

    const configLimit = window.AUTO_FETCH_TABLE_META_LIMIT;
    if (configLimit === 0) {
      return;
    }

    const numTablesToLoad = configLimit === -1 ? totalTables : Math.min(configLimit, totalTables);

    let completedTables = 0;

    for (let i = 0; i < numTablesToLoad; i++) {
      const eachTable = dataCatalogEntry.tables_meta[i];
      console.log("loading " + eachTable.name);
      await delay(100);
      try {
        await fetchColumnsData(databaseName, eachTable.name, data.entry);
        completedTables++;
      } catch (error) {
        console.error("Error loading table: " + eachTable.name, error);
        continue; // Skip to the next iteration if there is an error
      }
      const progress = Math.floor((completedTables / numTablesToLoad) * 100);
      localStorage.setItem('database_cache_progress_' + databaseName, progress);
    }
  });
}

