---
title: Django用のより良いPyGreSQlをサポート
author: Hue Team
type: post
date: 2014-03-28T04:10:47+00:00
url: /django用のより良いpygresqlをサポート/
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
slide_template:
  - default
sf_custom_excerpt:
  - |
    <p id="docs-internal-guid-4b2195c3-54dc-08d4-5d6f-c137c78b95a2"><span><a href="https://github.com/abec/django-pygresql">django-pygresql</a> のリリースにより、 </span><a href="https://gethue.com"><span>Hue</span></a><span> チームは</span><span> </span><span><a href="https://www.djangoproject.com/">Django</a>の <a href="http://www.pygresql.org/">PyGreSQL</a> のサポートを最初に試みてきました。 </span><span>
    </span></p>
    <h1><span>‘なぜ’ </span></h1>
    <span>オープンソースの世界には多くの異なった種類のライセンスがあり...
categories:
  - Programming
  - SDK

---
<p id="docs-internal-guid-4b2195c3-54dc-08d4-5d6f-c137c78b95a2">
  <span><a href="https://github.com/abec/django-pygresql">django-pygresql</a>のリリースにより、</span><a href="https://gethue.com"><span>Hue</span></a><span>チームは</span><span><a href="https://www.djangoproject.com/">Django</a>の<a href="http://www.pygresql.org/">PyGreSQL</a>のサポートを最初に試みてきました。 </span><span><br /> </span>
</p>

# <span>‘なぜ’ </span>

<span>オープンソースの世界には多くの異なった種類のライセンスがあり、あなたにとってどれが筋が通っているのかを知るのを混乱させます。</span>PyGreSQLは、パッケージして同梱するのに十分許容できるライセンスの[PostgreSQL][1]クライアントです。

# <span>‘どのように’ </span>

<span>PyGreSQLは、postgresqlバックエンドにより提供されているものと、いくつかのわずかな違いがあります。 これにはいくつかの変更が必要です: </span>

  * <span>Django で動作するための</span>Date/Datetime/Time型の操作
  * <span>データを操作するためのカスタムカーソル</span>
  * <span>カスタムの自動コミット管理</span>

<span>このバックエンドをインストールするために:</span>

  1. <span><a href="https://github.com/abec/django-pygresql/archive/master.zip">django-pygresql</a>をダウンロード</span><span><br /> </span>
  2. <span>実行</span> <pre class="code">unzip master.zip && cd django-pygresql-master && /build/env/bin/python install setup.py</pre>

  3. <span><hue root>/desktop/core/src/desktop/settings.pyの最下部に、以下のコードを追加:</span>

<pre class="code">if DATABASES['default']['ENGINE'] == 'django_pygresql':
  SOUTH_DATABASE_ADAPTERS = {
    'default': 'south.db.postgresql_psycopg2'
  }</pre>

<ol start="4">
  <li>
    <span>hue.iniに、desktop->database->engineを“django_pygresql”にセット。それから、通常のpostgresql設定パラメータを追加</span>
  </li>
</ol>

# <span>まとめ</span>

<span>これはPyGreSQL経由でPostgreSQLとやり取りするために、Djangoのバックエンドの最初の実装です。私たちは、これが他のコミュニティのメンバーに役立つことを願っています。</span>

[<span>hue-user</span>][2]<span> メーリングリスト、または</span><span><a href="https://twitter.com/gethue">@gethue</a>でお知らせ下さい!</span><span><br /> </span>

 [1]: http://www.postgresql.org/
 [2]: http://groups.google.com/a/cloudera.org/group/hue-user