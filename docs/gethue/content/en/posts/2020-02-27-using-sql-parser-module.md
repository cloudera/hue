---
title: Re-using the JavaScript SQL Parser
author: Romain
type: post
date: 2020-02-27T02:36:35+00:00
url: /blog/2020-02-27-using-sql-parser-module/
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.7
  - Development

---

## SQL autocompletion

The parser is running on the client side and comes with just a few megabytes of JavaScript that are then cached by the browser. This provides a very [reactive & rich experience](/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/) to the end users and allows to import it as a module dependency.

While the dynamic content like the list of tables, columns.. is obviously fetched via [remote endpoints](https://docs.gethue.com/developer/api/#sql-querying), all the SQL knowledge of the statements is available.

See the currently shipped [SQL dialects](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql).

### npm package

What if I only want to use only the autocomplete as a JavaScript module in my own app?

Importing the Parser can be simply done as a npm package. Here is an example on how to use the parser in a Node.js demo app. There are two ways to get the module:

* npm registry

Just get the module via:

    npm install gethue

Will install the latest from https://www.npmjs.com/package/gethue. Then import the parser you need with something like below and run it on an SQL statement:

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

* Local dependency

Checkout Hue and cd in the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep):

    cd tools/examples/api/hue_dep

    npm install
    npm run webpack
    npm run app

In `package.json` there's a dependency on Hue:

    "dependencies": {
      "hue": "file:../../.."
    },

Now let's import the Hive parser:

    import sqlAutocompleteParser from 'hue/desktop/core/src/desktop/js/parse/sql/hive/hiveAutocompleteParser';

### SQL scratchpad

The lightweight SQL Editor also called "Quick Query" comes as a [Web component](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/ko/components/contextPopover/ko.quickQueryContext.js). This one is still very new and will get better in the coming months.

!["Mini SQL Editor component"](https://cdn.gethue.com/uploads/2020/02/quick-query-component.jpg)


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Romain, from the Hue Team
