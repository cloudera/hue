---
title: Sqlスクラッチパッドコンポーネントとパブリック REST API を使用して、5 分で独自の SQL エディター (BYOE) を構築する
author: Hue Team
type: post
date: 2021-05-29T00:00:00+00:00
url: /blog/2021-05-29-create-own-sql-editor-via-webcomponent-and-public-api
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
  - Version 4.10
  - Development
  - Query
---

Hueの新しいSQLスクラッチパッドWebコンポーネントとREST APIを、プロジェクトに活用する。

[HueのSQL Editor](https://gethue.com/)プロジェクトは、[10年以上](https://gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/)にわたって進化し続けており、あらゆるデータベースやデータウェアハウスへのクエリを実行できます。 プロジェクト全体を完全に分離されたコンポーネントに分割したことが、急速に進化し、長い間生き続けることができた理由の一つです。

既に人気のある[SQL Parser](https://docs.gethue.com/developer/components/parsers/) コンポーネントに、 [SQL スクラッチパッド](https://docs.gethue.com/developer/components/scratchpad/) コンポーネントが加わりました。

![The SQL Scratchpad is a lightweight repackaging of the mature Hue SQL Editor](https://cdn-images-1.medium.com/max/2494/0*XnfuFshfdqc9vX74.png)*SQL スクラッチパッドは、成熟したHueのSQLエディタの軽量の再パッケージング*
> <sql-scratchpad />

主な追加の利点は、エディタの共有と統合が容易になったことです。したがって、エンドユーザにとって、より良い単一のエディタを作ることに集中するのではなく、車輪を再発明して様々な重複するSQLエディタを再作成することを避けるための、強力なケースとなります。

ここでは、コンポーネントの追加がいかに簡単であるかを示すライブデモを紹介します。

![Adding the component in 3 lines and watching the interaction with the public API of demo.gethue.com](https://cdn-images-1.medium.com/max/2356/1*yXRjYQN_eRUimzlXPl5SwQ.gif)*3行でコンポーネントを追加し、demo.gethue.com の公開API との連携を確認する*

### 仕組み

![The SQL Editor is a module published to a registry called NPM. The component can then be integrated in any Web page. It then communicates via a REST API with the Hue server which interacts with the Databases we want to query.](https://cdn-images-1.medium.com/max/2242/1*stLGGVTXa_V_PK2s1i6vIQ.png)*SQLエディタは、NPMというレジストリに公開されたモジュールです。 コンポーネントは、任意のWebページに統合することができます。 その後SQLエディタは、クエリを行いたいデータベースとやり取りするHueサーバーと、REST APIを介して通信します。*

**クエリエディタのコンポーネント**

このコンポーネントをWebページに統合するのは簡単です。 以下のHTMLコードをindex.htmlファイルにコピーして貼り付け、FireFoxで開いてください。

    <!DOCTYPE html>
    <html>
    
    <head>
      <title>SQL Scratchpad</title>
      <script type="text/javascript" src="https://unpkg.com/gethue/lib/components/SqlScratchpadWebComponent.js"></script>
    </head>
    
    <body>
      <div style="position: absolute; height: 100%; width: 100%">
        <sql-scratchpad api-url="https://demo.gethue.com" username="demo" password="demo" dialect="hive" />
      </div>
    </body>
    
    </html>

そして「それだけです」！

![ローカルの HTML ページを Firefox で直接開く](https://cdn-images-1.medium.com/max/2000/1*JzVbsWHqzZPI2pEAhG2mwQ.png) <br>*ローカルの HTML ページを Firefox で直接開く*

オートコンプリートはローカルパーサによって動作し、表示されます。 これは明らかに、自分自身ではSQL構文の手助けしかできません。 テーブルやカラムのリストのような動的コンテンツを取得して SQL クエリを実行するには、コンポーネントがクエリ API を指す必要があります。

次のステップとコンポーネントをより深く統合については、 [NPM Hueレジストリ](https://www.npmjs.com/package/gethue) を参照してください。

**クエリエディタAPI**

エディタコンポーネントを真に生かすためには、ユーザーを認証してクエリを実行するサービスと対話する必要があります。

これを可能にするのが、新しい [パブリック REST API](https://docs.gethue.com/developer/api/rest/#execute-a-query) であり、これまでよりもずっと簡単に使用できます。 これは通常のログインページとまったく同じ認証を利用しており、その後JWTトークンを提供するだけですみます。

たとえば、以下のようにアクセストークンを要求するだけです。

    curl -X POST https://demo.gethue.com/api/token/auth -d 'username=demo&password=demo'

その後、以下の各コールでトークンの値を指定します。

    curl -X POST https://demo.gethue.com/api/editor/execute/hive --data 'statement=SHOW TABLES' -H "Authorization: Bearer <token value>"

SQL クエリを実行するためのエンドポイントは大幅に簡素化され、SQL 方言とクエリステートメント、または以前に実行のために送信されたクエリの ID などの必要な情報のみが要求されるようになりました。

    curl -X POST https://demo.gethue.com/api/editor/check_status --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

この最初のリリースでは、SQLコンテンツの編集と実行が可能です。 完全なエディタの一般的な機能が徐々に統合されていますが、例えば以下のような機能があります。

* クエリの書式設定と共有
* 結果のダウンロード
* ポップアップでスクラッチパッドを開く(例：PySparkでの埋め込みSQLの編集)

認証情報を必要としないようにするために、SSO とローカルの JWT トークンを検証するオプションも近日公開予定です。

[SQLスクラッチパッドンポーネント](https://docs.gethue.com/developer/components/scratchpad/) とそのAPIは急速に進化しています。 今こそお試しいただいて、 [フィードバック](https://github.com/cloudera/hue/issues) を送っていただいたり、貢献していただくための絶好の機会です！

どうぞよろしくお願いします！

Romain from the Hue Team
