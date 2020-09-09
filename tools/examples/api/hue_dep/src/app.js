
import sqlAutocompleteParser from 'hue/desktop/core/src/desktop/js/parse/sql/hive/hiveAutocompleteParser';

const beforeCursor = 'SELECT col1, col2, tbl2.col3 FROM tbl; '; // Note extra space at end
const afterCursor = '';
const dialect = 'hive';
const debug = false;

console.log(
  JSON.stringify(
    sqlAutocompleteParser.parseSql(beforeCursor, afterCursor, dialect, debug),
    null,
    2
  )
);
