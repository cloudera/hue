---
title: "SQL Parsers"
draft: false
---

Parsers generated are JavaScript modules. This makes it easy to import a parser into your own apps (e.g. Webapp, Node.Js...). Importing a parser can be simply done via a npm package.

Here is an example on how to use the Hive parser:

    npm install --save gethue

Will install the latest from https://www.npmjs.com/package/gethue. Currently webpack needs to be used. An example of `webpack.config.js` can be found in the demo app [README](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/README.md#gethue).

Then import the parser you need with something like below and run it on an SQL statement:

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

Which then will output keywords suggestions and all the known locations:

    { locations:
      [ { type: 'statement', location: [Object] },
        { type: 'statementType',
          location: [Object],
          identifier: 'SELECT' },
        { type: 'selectList', missing: false, location: [Object] },
        { type: 'column',
          location: [Object],
          identifierChain: [Array],
          qualified: false,
          tables: [Array] },
        { type: 'column',
          location: [Object],
          identifierChain: [Array],
          qualified: false,
          tables: [Array] },
        { type: 'column',
          location: [Object],
          identifierChain: [Array],
          qualified: false,
          tables: [Array] },
        { type: 'table', location: [Object], identifierChain: [Array] },
        { type: 'whereClause', missing: true, location: [Object] },
        { type: 'limitClause', missing: true, location: [Object] } ],
      lowerCase: false,
      suggestKeywords:
      [ { value: 'ABORT', weight: -1 },
        { value: 'ALTER', weight: -1 },
        { value: 'ANALYZE TABLE', weight: -1 },
        { value: 'CREATE', weight: -1 },
        { value: 'DELETE', weight: -1 },
        { value: 'DESCRIBE', weight: -1 },
        { value: 'DROP', weight: -1 },
        { value: 'EXPLAIN', weight: -1 },
        { value: 'EXPORT', weight: -1 },
        { value: 'FROM', weight: -1 },
        { value: 'GRANT', weight: -1 },
        { value: 'IMPORT', weight: -1 },
        { value: 'INSERT', weight: -1 },
        { value: 'LOAD', weight: -1 },
        { value: 'MERGE', weight: -1 },
        { value: 'MSCK', weight: -1 },
        { value: 'RELOAD FUNCTION', weight: -1 },
        { value: 'RESET', weight: -1 },
        { value: 'REVOKE', weight: -1 },
        { value: 'SELECT', weight: -1 },
        { value: 'SET', weight: -1 },
        { value: 'SHOW', weight: -1 },
        { value: 'TRUNCATE', weight: -1 },
        { value: 'UPDATE', weight: -1 },
        { value: 'USE', weight: -1 },
        { value: 'WITH', weight: -1 } ],
      definitions: [] }
