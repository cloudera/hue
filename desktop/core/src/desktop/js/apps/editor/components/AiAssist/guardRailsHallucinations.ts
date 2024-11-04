import sqlParserRepository from 'parse/sql/sqlParserRepository';

// Types & Interfaces
import { LOCATION_TYPES } from 'parse/sql/sqlParseUtils';
import { IdentifierLocation, AutocompleteParser } from 'parse/types';
import { DbTableDetails } from 'api/apiAIHelper';

// CTE column aliases are viewed as columns by the parser when referenced
// outside the CTE, so we need to exclude them from the list of columns
const excludeCteColumnAliases = (
  locations: Array<IdentifierLocation>,
  columnNames: Array<string>
) => {
  let columnAliases: Array<string> = [];
  if (locations.find(loc => loc.identifier === 'WITH')) {
    columnAliases = locations
      .filter(loc => loc.type === LOCATION_TYPES.ALIAS && loc.source == LOCATION_TYPES.COLUMN)
      .map(loc => loc.alias || '');
  }
  return columnNames.filter(name => !columnAliases.includes(name));
};

const extractColumnsFromSql = (autocompleteParser: AutocompleteParser, sql: string) => {
  const result = autocompleteParser.parseSql(sql + ' ', '', true);
  const locations = result.locations;
  const columnLocations = locations?.filter(loc => loc.type === LOCATION_TYPES.COLUMN);
  const columnNames = columnLocations.map(
    loc => loc.identifierChain && loc.identifierChain[0].name
  ) as Array<string>; // Type assertion because we know that all column locations have an identifierChain

  const uniqueColumnNames = [...new Set(columnNames)];
  const finalResult = excludeCteColumnAliases(locations, uniqueColumnNames);
  return finalResult;
};

const extractTablesFromSql = (autocompleteParser: AutocompleteParser, sql: string) => {
  const result = autocompleteParser.parseSql(sql + ' ', '', true);
  const locations = result.locations;

  const tableLocations = locations.filter(loc => loc.type === LOCATION_TYPES.TABLE);
  const tableNames = tableLocations.map(
    loc => loc.identifierChain && loc.identifierChain[loc.identifierChain.length - 1].name
  ) as Array<string>;
  const uniqueTableNames = [...new Set(tableNames)];
  return uniqueTableNames;
};

const extractIdentifiersFromDbTableDetails = (dbTableDetails: DbTableDetails[]) => {
  const uniqueTableNames = new Set<string>();
  const uniqueColumnNames = new Set<string>();

  dbTableDetails.forEach(db =>
    db.tables.forEach(table => {
      uniqueTableNames.add(table.name);
      table.columns.forEach(col => uniqueColumnNames.add(col.name));
    })
  );

  return [[...uniqueTableNames], [...uniqueColumnNames]];
};

export const findHallucinations = async ({
  sql,
  dialect,
  dbTableDetails
}: {
  sql: string;
  dialect: string;
  dbTableDetails: DbTableDetails[];
}): Promise<{ columns: Array<string>; tables: Array<string> }> => {
  const autocompleteParser = await sqlParserRepository.getAutocompleteParser(dialect);

  // TODO: Consider db -> table -> column relation instead of a flat check

  const [availableTables, availableColumns] = extractIdentifiersFromDbTableDetails(dbTableDetails);

  const referencedColumns = extractColumnsFromSql(autocompleteParser, sql);
  const missingColumns = referencedColumns.filter(column => !availableColumns.includes(column));

  const referencedTables = extractTablesFromSql(autocompleteParser, sql);
  const missingTables = referencedTables.filter(column => !availableTables.includes(column));

  return { columns: missingColumns, tables: missingTables };
};
