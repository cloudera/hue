---
title: 実際のセキュリティのためにImpalaアプリでSentryを使用する
author: Hue Team
type: post
date: 2013-12-16T23:59:48+00:00
url: /実際のセキュリティのためにimpalaアプリでsentryを使用/
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
  - Apache Sentry (incubating) は、Hadoopでデータをクエリする時にセキュリティを提供する新しい方法です（例：SELECTやCREATEのSQLステートメントでの権限）。Impalaは...
categories:
  - Enterprise
  - Impala

---
<p id="docs-internal-guid-2146a2cd-fca2-7325-b82b-68ed6ae64ad9">
  <a href="http://incubator.apache.org/projects/sentry.html"><span>Apache Sentry</span></a><span> (incubating) は、Hadoopでデータをクエリする時にセキュリティを提供する新しい方法です（例：SELECTやCREATEのSQLステートメントでの権限）。</span><span><a href="http://impala.io/">Impala</a>はApache Hadoopに</span><span><a href="https://gethue.com/fast-sql-with-the-impala-query-editor">高速なSQL</a>を提供しており、Sentryを利用することができます。以下は</span><span><a href="https://gethue.com">Hue</a>でSentryを使用する方法です。</span><span><br /> </span>
</p>

&nbsp;

<span>最初に、Proxyとして動作する&#8217;hue&#8217;ではなく現在のユーザーに対して権限をチェックするように、</span>[<span>hue.ini</span>][1]<span> の詐称(impersonation)を有効にします:</span>

&nbsp;

<pre>[impala]   
   impersonation_enabled=True</pre>

<span>そうすると、このエラーになるかもしれません:</span>

<pre>User 'hue' is not authorized to impersonate 'romain'. User impersonation is disabled.</pre>

&nbsp;

<span>これはHueがproxyとして権限を与えられていないからです。これを修正するために、Impalaの起動時に次のフラグを指定します:</span>

<pre>--authorized_proxy_user_config=hue=*</pre>

&nbsp;

<span>注: Cloudera Managerを使用する場合、Impaladのコマンドラインの引数の安全バルブに追加します。</span>

&nbsp;

<span>これで<a href="https://gethue.com/hadoop-tutorial-hive-query-editor-with-hiveserver2-and">Hive</a>に似た実際のセキュリティからの恩恵が受けられます</span><span>!</span>

&nbsp;

<span>いつものように、コメントは</span><span><a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a>リスト、あるいは</span><span><a href="https://twitter.com/gethue">@gethue</a>ま</span>で!

&nbsp;

<span>注: CDH4/Hue 2.xの場合、HueがHiveServer2 APIでImpalaと通信するように設定されているかを確認して下さい:</span>

&nbsp;

<pre>[impala]
  # Host of the Impala Server (one of the Impalad)
  server_host=nightly-1.ent.cloudera.com

  # The backend to contact for queries/metadata requests.
  # Choices are 'beeswax' or 'hiveserver2' (default).
  # 'hiveserver2' supports log, progress information, query cancellation
  # 'beeswax' requires Beeswax to run for proxying the metadata requests
  server_interface=hiveserver2

  # Port of the Impala Server
  # Default is 21050 as HiveServer2 Thrift interface is the default.
  # Use 21000 when using Beeswax Thrift interface.
  server_port=21050

  # Kerberos principal
  ## impala_principal=impala/hostname.foo.com

  impersonation_enabled=True</pre>

 [1]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini