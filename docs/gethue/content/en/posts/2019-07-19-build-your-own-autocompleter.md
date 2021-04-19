---
title: BYOA – Build Your Own Autocompleter
author: Hue Team
type: post
date: 2019-07-19T18:45:43+00:00
url: /build-your-own-autocompleter/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
  - Development
  # - Version 4.5

---
Hue is a SQL Editor integrating with the most common [data warehouses and databases.][1] Getting specialized autocomplete for each language brings better code maintainability (force a decoupled design), speed (no need to load all the parsers for only one language) and obviously a nicer end user experience (Impala, Hive, PostgreSQL&#8230; always have slight different syntax).

In Hue we use generated parsers to handle autocomplete and syntax checking in the editors. In this post we&#8217;ll guide you through the steps necessary to create an autocompleter for any SQL dialect in Hue.

There are currently three parsers for this in Hue, one for Impala, one for Hive and a generic SQL parser that is used for other dialects. The parsers are written using a [bison][2] grammar and are generated with [jison][3]. They&#8217;re 100% javascript and live on the client side, this gives the performance of a desktop editor in your browser.

## Structure

Normally parsers generate a parse tree but for our purposes we don&#8217;t really care about the statement itself but rather about what should happen when parts of a particular statement is encountered. During parsing the state is kept outside the parse tree and in case of syntax errors this enables us to provide some results up to the point of the error. There are two ways that incomplete/erroneous statements are handled, first we try to define most of the incomplete grammar and secondly we rely on the &#8220;error&#8221; token which allows the parser to recover.

The parsers provide one function, `parseSql`, that accepts the text before the cursor and the text after the cursor as arguments. The function returns an object containing instructions on what to suggest given the input.

As an example:

<pre><code class="javascript">sqlParserRepository.getAutocompleteParser('impala').then(parser =&gt; {
    console.log(parser.parseSql('SELECT * FROM customers'));
  });
</code></pre>

Would output something like:

<pre><code class="javascript">{
    definitions: [],
    locations: (6) [{…}, {…}, {…}, {…}, {…}, {…}],
    lowerCase: false,
    suggestAggregateFunctions: {tables: [Array(1)]},
    suggestAnalyticFunctions: true,
    suggestColumns: {source: "select", tables: [{identifierChain: [{name: "customers"}]}]},
    suggestFunctions: {},
    suggestKeywords: (8) [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
  }
</code></pre>

We take this output and link it to various sources of metadata to provide the list of suggestions the user finally sees. In this case we&#8217;d use the data from &#8220;suggestColumns&#8221; to call the backend for all the columns of the &#8220;customers&#8221; table. We&#8217;d also use the functions library to list all the UDFs etc.

Here&#8217;s a list of some of the different types of suggestions the parser can identify:

<table style="margin-left: 20px; margin-bottom: 15px; border: none;" width="500">
  <tr>
    <td style="vertical-align: top; border: none;" width="250">
      suggestAggregateFunctions<br /> suggestAnalyticFunctions<br /> suggestColRefKeywords<br /> suggestColumnAliases<br /> suggestColumns<br /> suggestCommonTableExpressions<br /> suggestDatabases<br /> suggestFilters<br /> suggestFunctions<br /> suggestGroupBys
    </td>

    <td style="vertical-align: top; border: none;" width="250">
      suggestHdfs<br /> suggestIdentifiers<br /> suggestJoinConditions<br /> suggestJoins<br /> suggestKeywords<br /> suggestOrderBys<br /> suggestSetOptions<br /> suggestTables<br /> suggestValues
    </td>
  </tr>
</table>

Parsers are generated and added to the repository using our custom cli app `generateParsers.js` under tools/jison/. To for instance generate all the Impala parsers you would run the following command in the hue folder:

<pre><code class="bash">node tools/jison/generateParsers.js impala</code></pre>

In reality two parsers are generated per dialect, one for syntax and one for autocomplete. The syntax parsers is a subset of the autocomplete parser with no error recovery and without the autocomplete specific grammar.

All the jison grammar files can be found [here][4] and the generated parsers are also committed together with their tests [here][5].

## The grammar

In a regular SQL parser you might define the grammar of a select statement like this:

<pre>SelectStatement
    : 'SELECT' ColumnList 'FROM' Identifier
    ;

  ColumnList
    : Identifier
    | ColumnList ',' Identifier
    ;
</pre>

This would be able to parse a statement like `'SELECT a, b, c FROM some_table'` (depending on lexer definitions of course). To turn this into an autocompleter we add the notion of a cursor to the mix, it&#8217;s defined as an obscure character that’s unlikely to be used in a statement. We went for `'\u2020'`, the dagger, identified as `'CURSOR'` in the lexer. The actual parsed string is therefore `beforeCursor + ‘\u2020’ + afterCursor.`

For the statement above we&#8217;d add an extra rule with an _EDIT postfix like this:

<pre>SelectStatement
    : 'SELECT' ColumnList 'FROM' Identifier
    ;

  SelectStatement_EDIT
    : 'CURSOR' --&gt; { suggestKeywords: ['SELECT'] }
    | 'SELECT' ColumnList_EDIT
    | 'SELECT' ColumnList 'CURSOR' --&gt; { suggestKeywords: ['FROM'] }
    | 'SELECT' ColumnList 'FROM' 'CURSOR'  --&gt; { suggestTables: {} }
    | 'SELECT' ColumnList_EDIT 'FROM' Identifier --&gt; { suggestColumns: { table: $4 } }
    ;
</pre>

So if a &#8220;lonely&#8221; cursor is encountered it will tell us to suggest the &#8216;SELECT&#8217; keyword etc.

## Tutorial: Creating a basic PostgreSQL parser in 5 minutes

Prerequisites: make sure you have [jison installed][6] and a [development Hue][7]. Then configure a [PostgreSQL interpreter][8].

In the Hue folder:

./build/env/bin/pip install psycopg2-binary</pre>

and edit your hue config `desktop/conf/pseudo-distributed.ini` to contain:

<pre><code class="bash">[notebook]
   [[interpreters]]
    [[[postgresql]]]
      name = postgresql
      interface=sqlalchemy
      options='{";url&amp;amp;quot;: &amp;amp;quot;postgresql://hue:pwd@dbhost:31335/huedb"}'
</code></pre>

Our generateParsers tool can take an existing dialect and setup the source code for a new parsers based on that.

In the hue folder run:

<pre><code class="bash">node tools/jison/generateParsers.js -new generic postgresql</code></pre>

After the -new argument you specify an existing dialect to clone first and then the name of the new parser.

Once executed the tool has cloned the generic parser with tests and generated a new postgresql parsers. The jison files can be found under `desktop/core/src/desktop/js/parse/jison/sql/postgresql/` and the tests can be found in `desktop/core/src/desktop/js/parse/sql/postgresql/test`

To regenerate the parsers after changes to the jison files run:

<pre><code class="bash">node tools/jison/generateParsers.js postgresql</code></pre>

The tool will report any problems with the grammar. Note that it might still generate a parser if the grammar isn&#8217;t ambiguous but it&#8217;s likely that there will be test failures.

### Extending the grammar

This gives you an idea on how to add custom syntax to the newly generated postgresql parser. For this example we&#8217;ll add the [REINDEX][9] statement as it&#8217;s quite simple.

<pre><code class="bash">REINDEX { INDEX | TABLE | DATABASE | SYSTEM } name [ FORCE ]</code></pre>

We&#8217;ll start by adding a test, in `postgresqlAutocompleteParser.test.js` in the test folder inside the main describe function before the first &#8216;it(&#8220;should &#8230;&#8217;:

<pre><code class="javascript">fdescribe('REINDEX', () =&gt; {
    it('should handle "REINDEX TABLE foo FORCE; |"', () =&gt; {
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

    it('should suggest keywords for "REINDEX |"', () =&gt; {
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
</code></pre>

When we now run `npm run test` there should be two failing tests.

Next we&#8217;ll have to add the keyword to the lexer, let&#8217;s open `sql.jisonlex` in the jison folder for postgresql and add the following new tokens:

<pre>'REINDEX'                                  { parser.determineCase(yytext); return 'REINDEX'; }
'INDEX'                                    { return 'INDEX'; }
'SYSTEM'                                   { return 'SYSTEM'; }
'FORCE'                                    { return 'FORCE'; }
</pre>

Now let&#8217;s add the grammar, starting with the complete specification. For simplicity we&#8217;ll add it in `sql_main.jison`, at the bottom of the file add:

<pre>DataDefinition
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
</pre>

&#8220;DataDefinition&#8221; is an existing rule and this extends that rule with &#8220;ReindexStatement&#8221;.

Save the file(s) and first run `node tools/jison/generateParsers.js postgresql` then `npm run test` and we should be down to one failing test.

For the next one we&#8217;ll add some keyword suggestions after the user has typed REINDEX, we&#8217;ll continue below the `ReindexStatement` in `sql_main.jison`:

<pre>DataDefinition_EDIT
 : ReindexStatement_EDIT
 ;

ReindexStatement_EDIT
 : 'REINDEX' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'INDEX', 'SYSTEM', 'TABLE']);
   }
 ;
</pre>

Again, run `node tools/jison/generateParsers.js postgresql` then `npm run test` and the tests should both be green.

We also want the autocompleter to suggest the keyword REINDEX when the user hasn&#8217;t typed anything, to do that let&#8217;s first add the following test with the other new ones in `postgresqlAutocompleteParserSpec.js`:

<pre><code class="javascript">it('should suggest REINDEX for "|"', () =&gt; {
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
</code></pre>

For this to pass we need to add `REINDEX` to the list of DDL and DML keywords in the file `sqlParseSupport.js` next to the generated parser (`desktop/core/src/desktop/js/parse/sql/postgresql/sqlParseSupport.js/`). Find the function `parser.suggestDdlAndDmlKeywords` and add &#8216;REINDEX&#8217; to the keywords array. Now run `npm run test` and the three tests should pass.

Before you continue further be sure to remove the &#8216;f&#8217; from &#8216;fdescribe&#8217; in the spec to allow all other tests to run. Note that in this case there will be two new failing tests where the keyword &#8216;REINDEX&#8217; has to be added.

In order to use the newly generated parsers we have to add them to the webpack bundles:

<pre><code class="bash">npm run webpack
npm run webpack-workers</code></pre>

While developing it will speed up if the webpack bundling runs in the background, for this open two terminal sessions and run on `npm run dev` in one and `npm run dev-workers` in the other. It will then monitor changes to the files and build a lot quicker.

After the bundling you can now test it directly in the editor:

<div style="margin-bottom: 10px;">
  <a href="https://cdn.gethue.com/uploads/2019/07/Screenshot-2019-07-18-11.13.50.png"><img class="aligncenter size-full wp-image-5989" src="https://cdn.gethue.com/uploads/2019/07/Screenshot-2019-07-18-11.13.50.png" alt=""  /></a>
</div>

We hope this will get you to dive in to the wonderful world of autocompleters and grammars! Looking for a good project? Integrating [Apache Calcite][10], [ZetaSql][11], [PartiQL][12]&#8230; would make SQL users even happier with a lot more Databases!

And as always, if you have any feedback or questions then feel free to comment here or on [@gethue][13]!

 [1]: https://docs.gethue.com/administrator/configuration/editor/
 [2]: https://www.gnu.org/software/bison/
 [3]: https://github.com/zaach/jison
 [4]: https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/jison/sql
 [5]: https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql
 [6]: https://docs.gethue.com/developer/development/#sql-autocomplete
 [7]: https://docs.gethue.com/administrator/installation/dependencies/
 [8]: https://docs.gethue.com/administrator/configuration/editor/#postgresql
 [9]: https://www.postgresql.org/docs/9.1/sql-reindex.html
 [10]: https://calcite.apache.org/docs/reference.html
 [11]: https://github.com/google/zetasql
 [12]: https://partiql.org/tutorial.html
 [13]: https://twitter.com/gethue
