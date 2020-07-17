

https://docs.gethue.com/developer/api/#sql-autocompletion

    npm install gethue


    import sqlAutocompleteParser from 'gethue/parse/sql/hive/hiveAutocompleteParser';

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
