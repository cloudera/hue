---
title: "SQL Parsers"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

The parsers are the flagship part of Hue and power extremely advanced autocompletes and other [SQL functionalities](/user/querying/#autocomplete). They are running on the client side and comes with just a few megabytes of JavaScript that are cached by the browser. This provides a very reactive experience to the end user and allows to [import them](#using-hue-parsers-in-your-project) as classic JavaScript modules for your own development needs.

While the dynamic content like the list of tables, columns is obviously fetched via [remote endpoints](#sql-querying), all the SQL knowledge of the statements is available.

See the currently shipped [SQL dialects](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql).

This guide takes you through the steps necessary to create an autocompleter for any [SQL dialect](/administrator/configuration/connectors/#databases) in Hue. The major benefits are:

* Proposing only valid syntax in the autocomplete
* Getting the list of tables, columns, UDFs... automatically
* Suggesting fixes
* Diffing, formatting... queries

## Parser Theory

There are several parsers in Hue already (e.g. one for Impala, one for Hive..) and a generic SQL that is used for other dialects. The parsers are written using a [bison](https://www.gnu.org/software/bison/) grammar and are generated with [jison](https://github.com/zaach/jison). They arere 100% Javascript and live on the client side, this gives the performance of a desktop editor in your browser.

Building a dedicated work is more effort but it then allows a very rich end user experience, e.g.:

* Handle invalid/incomplete queries and propose suggestions/fixes
* date_column = <Date compatible UDF ...>
* Language reference or data samples just by pointing the cursor on SQL identifiers
* Leverage the parser for risk alerts (e.g. adding automatic LIMIT) or proper re-formatting

### Structure

Normally parsers generate a parse tree but for our purposes we don’t really care about the statement itself but rather about what should happen when parts of a particular statement is encountered. During parsing the state is kept outside the parse tree and in case of syntax errors this enables us to provide some results up to the point of the error. There are two ways that incomplete/erroneous statements are handled, first we try to define most of the incomplete grammar and secondly we rely on the “error” token which allows the parser to recover.

The parsers provide one function, parseSql, that accepts the text before the cursor and the text after the cursor as arguments. The function returns an object containing instructions on what to suggest given the input.

As an example:

    sqlParserRepository.getAutocompleter('impala').then(parser => {
      console.log(parser.parseSql('SELECT * FROM customers'));
    });

Would output something like:

    {
      definitions: [],
      locations: (6) [{…}, {…}, {…}, {…}, {…}, {…}],
      lowerCase: false,
      suggestAggregateFunctions: {tables: [Array(1)]},
      suggestAnalyticFunctions: true,
      suggestColumns: {source: "select", tables: [{identifierChain: [{name: "customers"}]}]},
      suggestFunctions: {},
      suggestKeywords: (8) [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
    }

We take this output and link it to various sources of metadata to provide the list of suggestions the user finally sees. In this case we’d use the data from “suggestColumns” to call the backend for all the columns of the “customers” table. We’d also use the functions library to list all the UDFs etc.

Here’s a list of some of the different types of suggestions the parser can identify:

    suggestAggregateFunctions
    suggestAnalyticFunctions
    suggestColRefKeywords
    suggestColumnAliases
    suggestColumns
    suggestCommonTableExpressions
    suggestDatabases
    suggestFilters
    suggestFunctions
    suggestGroupBys	suggestHdfs
    suggestIdentifiers
    suggestJoinConditions
    suggestJoins
    suggestKeywords
    suggestOrderBys
    suggestSetOptions
    suggestTables
    suggestValues

Parsers are generated and added to the repository using the command generateParsers.js under tools/jison/. To for instance generate all the Impala parsers you would run the following command in the hue folder:

    node tools/jison/generateParsers.js impala

In reality two parsers are generated per dialect, one for syntax and one for autocomplete. The syntax parsers is a subset of the autocomplete parser with no error recovery and without the autocomplete specific grammar.

All the jison grammar files can be found [here](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/jison/sql) and the generated parsers are also committed together with their tests [here](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql).

### The grammar

In a regular SQL parser you might define the grammar of a select statement like this:

    SelectStatement
      : 'SELECT' ColumnList 'FROM' Identifier
      ;

    ColumnList
      : Identifier
      | ColumnList ',' Identifier
      ;

This would be able to parse a statement like 'SELECT a, b, c FROM some_table' (depending on lexer definitions of course).

### Notion of cursor

To turn this into an autocompleter we add the notion of a cursor. Often, the user has the cursor somewhere in the statement. In the previous section, we were assuming that the query was already typed and the user had not mouse cursor within it.

The cursor is represented as an obscure character that is unlikely to be used in a statement. Currently '\u2020' was picked, the dagger, identified as 'CURSOR' in the lexer. The actual parsed string is therefore beforeCursor + ‘\u2020’ + afterCursor.

For the statement above we’d add an extra rule with an _EDIT postfix like this:

    SelectStatement
      : 'SELECT' ColumnList 'FROM' Identifier
      ;

    SelectStatement_EDIT
      : 'CURSOR' --> { suggestKeywords: ['SELECT'] }
      | 'SELECT' ColumnList_EDIT
      | 'SELECT' ColumnList 'CURSOR' --> { suggestKeywords: ['FROM'] }
      | 'SELECT' ColumnList 'FROM' 'CURSOR'  --> { suggestTables: {} }
      | 'SELECT' ColumnList_EDIT 'FROM' Identifier --> { suggestColumns: { table: $4 } }
      ;

So for example if a cursor without any text is encountered, it will tell us to suggest the ‘SELECT’ keyword etc.

## Tutorial: Creating a parser

The goal is to create from scratch a new parser for the PostgreSQL database.

### Prerequisites

Make sure you have [jison](/developer/development/#sql-autocomplete) installed and a [development](/administrator/installation/dependencies/) Hue. Then configure a [PostgreSQL interpreter](/administrator/configuration/connectors/#postgresql).

In the Hue folder:

    ./build/env/bin/pip install psycopg2-binary

and edit your hue config desktop/conf/pseudo-distributed.ini to contain:

    [notebook]
    [[interpreters]]
      [[[postgresql]]]
        name = postgresql
        interface=sqlalchemy
        options='{"url": "postgresql://hue:hue@host:31335/hue"}'

Our generateParsers tool can take an existing dialect and setup the source code for a new parsers based on that.

In the hue folder run:

    node tools/jison/generateParsers.js -new generic postgresql

After the -new argument you specify an existing dialect to clone first and then the name of the new parser.

Once executed the tool has cloned the generic parser with tests and generated a new postgresql parsers. The jison files can be found under `desktop/core/src/desktop/js/parse/jison/sql/postgresql/` and the testscan be found in `desktop/core/src/desktop/js/parse/sql/postgresql/test`.

To regenerate the parsers after changes to the jison files run:

    node tools/jison/generateParsers.js postgresql

The tool will report any problems with the grammar. Note that it might still generate a parser if the grammar isn’t ambiguous but it’s likely that there will be test failures.

### Extending the grammar

This gives you an idea on how to add custom syntax to the newly generated postgresql parser. For this example we’ll add the [REINDEX](https://www.postgresql.org/docs/9.1/sql-reindex.html) statement as it’s quite simple.

    REINDEX { INDEX | TABLE | DATABASE | SYSTEM } name [ FORCE ]

We’ll start by adding a test, in `postgresqlAutocompleteParser.test.js` in the test folder inside the main describe function before the first `it('should...`:

    describe('REINDEX', () => {
      it('should handle "REINDEX TABLE foo FORCE; |"', () => {
        assertAutoComplete({
          beforeCursor: 'REINDEX TABLE foo FORCE;  ',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "REINDEX |"', () => {
        assertAutoComplete({
          beforeCursor: 'REINDEX ',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['INDEX', 'DATABASE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

When we now run `npm run test -- postgresqlAutocompleteParser.test.js` there should be two failing tests.

Alternatively, if using Jest directly and working on parsers currently being skipped in the CI, provide matching file names and an empty blacklist file pattern. e.g.:

    jest calciteAutocompleteParser.Select.stream.test.js --testPathIgnorePatterns=[]
    jest calciteAutocompleteParser --testPathIgnorePatterns=[]

Next we’ll have to add the keyword to the lexer, let’s open `sql.jisonlex` in the jison folder for postgresql and add the following new tokens:

    'REINDEX'                                  { parser.determineCase(yytext); return 'REINDEX'; }
    'INDEX'                                    { return 'INDEX'; }
    'SYSTEM'                                   { return 'SYSTEM'; }
    'FORCE'                                    { return 'FORCE'; }

Now let’s add the grammar, starting with the complete specification. For simplicity we’ll add it in `sql_main.jison`, at the bottom of the file add:

    DataDefinition
    : ReindexStatement
    ;

    ReindexStatement
    : 'REINDEX' ReindexTarget RegularOrBacktickedIdentifier OptionalForce
    ;

    ReindexTarget
    : 'INDEX'
    | 'TABLE'
    | 'DATABASE'
    | 'SYSTEM'
    ;

    OptionalForce
    :
    | 'FORCE'
    ;

"DataDefinition" is an existing rule and this extends that rule with "ReindexStatement".

Save the files and first run `node tools/jison/generateParsers.js postgresql` then `npm run test -- postgresqlAutocompleteParser.test.js` and we should be down to one failing test.

For the next one we’ll add some keyword suggestions after the user has typed REINDEX, we’ll continue below the ReindexStatement in `sql_main.jison`:

    DataDefinition_EDIT
    : ReindexStatement_EDIT
    ;

    ReindexStatement_EDIT
    : 'REINDEX' 'CURSOR'
      {
        parser.suggestKeywords(['DATABASE', 'INDEX', 'SYSTEM', 'TABLE']);
      }
    ;

Again, run `node tools/jison/generateParsers.js postgresql` then `npm run test -- postgresqlAutocompleteParser.test.js` and the tests should both be green.

We also want the autocompleter to suggest the keyword REINDEX when the user hasn’t typed anything, to do that let’s first add the following test with the other new ones in `postgresqlAutocompleteParser.test.js`:

    it('should suggest REINDEX for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['REINDEX'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

For this to pass we need to add REINDEX to the list of DDL and DML keywords in the file `sqlParseSupport.js` next to the generated parser (`desktop/core/src/desktop/js/parse/sql/postgresql/sqlParseSupport.js/`). Find the function `parser.suggestDdlAndDmlKeywords` and add ‘REINDEX’ to the keywords array. Now run `npm run test -- postgresqlAutocompleteParser.test.js` and the three tests should pass.

Before you continue further, note that in this case there will be two new failing tests where the keyword ‘REINDEX’ has to be added.

In order to use the newly generated parsers we have to add them to the webpack bundles:

    npm run webpack
    npm run webpack-workers

While developing it will speed up if the webpack bundling runs in the background, for this open two terminal sessions and run `npm run dev` in one and `npm run dev-workers` in the other. It will then monitor changes to the files and build a lot quicker.

After the bundling you can now test it directly in the editor!

## Syntax highlighting

New keywords might not be properly colored highlighted in the editor. This is especially true when adding a new language. Here is how to fix that.

![Missing highlighting](https://cdn.gethue.com/docs/dev/syntax_highlighting_missing.png)

Missing highlighting for 'REINDEX' keyword

![With highlighting](https://cdn.gethue.com/docs/dev/syntax_highlighting_updated.png)

With correct highlighting

### Updating keywords

The Editor is currently visually powered by [Ace](https://ace.c9.io). The list of supported languages is found in the [mode](https://github.com/cloudera/hue/tree/master/tools/ace-editor/lib/ace/mode) directory.

For each dialect, we have two files. e.g. with PostgreSQL:

    pgsql.js
    pgsql_highlight_rules.js

The list of keywords is present in `*_highlight_rules.js` and can be updated there.

    var keywords = (
        "ALL|ALTER|REINDEX|..."
    )

Afterwards, run:

    make ace

And after refreshing the editor page, the updated mode will be activated.

### Adding new dialect

To add a new dialect, it is recommended to copy the two files of the closest mode and rename all the names inside. For example, if we were creating a new `ksql` mode, `pgsql_highlight_rules.js` would become `ksql_highlight_rules.js` and we would rename all the references inside to `psql` to `ksql`. Same with `pgsql.js` to `ksql.js`. In particular, the name of the mode to be referenced later is in:

    KsqlHighlightRules.metaData = {
      fileTypes: ["ksql"],
      name: "ksql",
      scopeName: "source.ksql"
    };

Tip: inheritance of modes is supported by Ace, which make it handy for avoiding potential duplications.

In the Editor, the mapping between Ace's modes and the type of snippets is happening in [editor_components.mako](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/templates/editor_components.mako#L2118).

In the KSQL case we have:

    ksql: {
      placeHolder: '${ _("Example: SELECT * FROM stream, or press CTRL + space") }',
      aceMode: 'ace/mode/ksql',
      snippetIcon: 'fa-database',
      sqlDialect: true
    },

And cf. above [prerequisites](#prerequisites), any interpreter snippet with `ksql` will pick-up the new highlighter:

      [[[ksql]]]
        name = KSQL Analytics
        interface=ksql

Note: after [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) we will be able to have multiple interpreters on the same dialect (e.g. pointing to two different databases of the same type).

## Reusing a parser in your project

The parsers ship as a pluggable [component](/developer/components/parsers).
