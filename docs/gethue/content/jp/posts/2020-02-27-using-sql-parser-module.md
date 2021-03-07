---
title: JavaScript SQL パーサーの再利用
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

## SQL の自動補完

パーサーはクライアント側で実行され、その後ブラウザーによってキャッシュされるわずか数メガバイトの JavaScriptが 付属しています。これにより、エンドユーザーにとても[リアクティブかつ豊富な経験](/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/)が提供され、モジュールの依存関係としてインポートできます。

テーブルや列の一覧のような動的コンテンツは[リモートのエンドポイント](https://docs.gethue.com/developer/api/#sql-querying)を介して取得されますが、ステートメントの全ての SQL の知見は利用可能です。

現在提供されている[SQLの方言](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql)をご参照下さい。

### npm パッケージ

自分のアプリで自動補完のみをJavaScript モジュールとして使用したい場合はどうしますか?

パーサーのインポートは npm パッケージとしてシンプルに行うことができます。これは Node.js [デモアプリ](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep) でパーサーを使用する方法の例です:

    cd tools/examples/api/hue_dep

    npm install
    npm run webpack
    npm run app

`package.json` には Hue の依存関係があります:

    "dependencies": {
      "hue": "file:../../.."
    },

GitHub のリンクにすることもできます。例えば "hue": "git://github.com/cloudera/hue.git” のようにしますが `npm install` には少し時間がかかります。

次に Hive パーサーをインポートして SQL ステートメントで実行します:

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

これにより、キーワードの候補と全ての既知の位置が出力されます:

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

### SQL スクラッチパッド

"Quick Query" とも呼ばれる軽量の SQL エディターは[Web コンポーネント](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/ko/components/contextPopover/ko.quickQueryContext.js) として提供されています。これはまだ非常に新しく、今後数カ月で良くなることでしょう。

!["Mini SQL Editor component"](https://cdn.gethue.com/uploads/2020/02/quick-query-component.jpg)


フィードバックや質問があれば、このブログや<a href="https://discourse.gethue.com/">フォーラム</a>にkメントしてください。また、<a href="https://docs.gethue.com/quickstart/">quick start</a> でSQLのクエリを行なってください!


Romain, from the Hue Team
