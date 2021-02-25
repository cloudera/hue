import sqlAutocompleteParser from './presto-parser-esm.js';

const beforeCursor = 'SELECT col1, col2, tbl2.col3 FROM tbl; '; // Note extra space at end
const afterCursor = '';
const dialect = 'presto';
const debug = true;

console.log(
  JSON.stringify(
    sqlAutocompleteParser.parseSql(beforeCursor, afterCursor, dialect, debug),
    null,
    2
  )
);