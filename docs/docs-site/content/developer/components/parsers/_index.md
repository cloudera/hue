---
title: "SQL Parsers"
draft: false
weight: 2
---

The parsers are the flagship part of Hue and power advanced autocompletes and other [SQL functionalities](/user/querying/#autocomplete).

Refer the [SQL Parser Documentation](/developer/development/#sql-parsers) for how they works and are built.

## Live Demo

{{< rawhtml >}}
  <link rel="stylesheet" href="demo/styles.css">
  <div class="live-parser-container">
    <div class="parser-scripts-container"></div>
    <select>
      <option value="hiveAutocompleteParser">Hive Autocomplete Parser</option>
      <option value="hiveSyntaxParser">Hive Syntax Error Parser</option>
      <option disabled> </option>
      <option value="impalaAutocompleteParser">Impala Autocomplete Parser</option>
      <option value="impalaSyntaxParser">Impala Syntax Error Parser</option>
      <option disabled> </option>
      <option value="calciteAutocompleteParser">Calcite Autocomplete Parser</option>
      <option value="calciteSyntaxParser">Calcite Syntax Error Parser</option>
      <option disabled> </option>
      <option value="elasticsearchAutocompleteParser">Elasticsearch Autocomplete Parser</option>
      <option value="elasticsearchSyntaxParser">Elasticsearch Syntax Error Parser</option>
      <option disabled> </option>
      <option value="phoenixAutocompleteParser">Phoenix Autocomplete Parser</option>
      <option value="phoenixSyntaxParser">Phoenix Syntax Error Parser</option>
      <option disabled> </option>
      <option value="druidAutocompleteParser">Druid Autocomplete Parser</option>
      <option value="druidSyntaxParser">Druid Syntax Error Parser</option>
      <option disabled> </option>
      <option value="flinkAutocompleteParser">Flink Autocomplete Parser</option>
      <option value="flinkSyntaxParser">Flink Syntax Error Parser</option>
      <option disabled> </option>
      <option value="ksqlAutocompleteParser">Ksql Autocomplete Parser</option>
      <option value="ksqlSyntaxParser">Ksql Syntax Error Parser</option>
      <option disabled> </option>
      <option value="prestoAutocompleteParser">Presto Autocomplete Parser</option>
      <option value="prestoSyntaxParser">Presto Syntax Error Parser</option>
      <option disabled> </option>
      <option value="genericAutocompleteParser">Generic Autocomplete Parser</option>
      <option value="genericSyntaxParser">Generic Syntax Error Parser</option>
    </select>
    <div class="live-message"></div>
    <label>Query <textarea>
      SELECT accountid,
            account.name,
            sum(expectedrevenue) AS expected,
            count(*) ct
      FROM sfdc.opportunity_history
      JOIN sfdc.account ON account.id = opportunity_history.accountid
      WHERE opportunity_history.`snapshottime` = '2017-09-25'
      GROUP BY accountid,
              account.name
      ORDER BY expected DESC
      LIMIT 100;
    </textarea></label>
    <label>Parsed Result <textarea readonly></textarea></label>
  </div>
  <script src="demo/live-parser.js"></script>
{{< /rawhtml >}}

## Import

Import the parser you need with something like below and run it on an SQL statement:

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

## Example

A full example on how to use the Hive parser can be found in the demo app [README](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/README.md).
