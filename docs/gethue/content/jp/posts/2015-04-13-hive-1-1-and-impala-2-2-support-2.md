---
title: Hive 1.1とImpala 2.2のサポート
author: Hue Team
type: post
date: 2015-04-13T09:41:49+00:00
url: /hive-1-1-and-impala-2-2-support-2/
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
sf_custom_excerpt:
  - Hiveは最終的にver1.0になったことで、大きくジャンプしました。それは現行のver 1.1（ver 0.14相当）でさえもです。これら一連の新機能のメリットを得るために、HueのHiveとImpalaエディタはアップグレードされました。
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
sf_remove_promo_bar:
  - 1
categories:
  - Hive
  - Hue 3.8
  - Impala

---
[Hive][1]は、最終的にver1.0になったことで大きくジャンプしました。それは現行のver 1.1（ver 0.14相当）でも同様です。これら一連の新機能のメリットを得るために、HueのHiveと[Impala][2]エディタがアップグレードされました。

[<img class="aligncenter size-large wp-image-2450" src="https://cdn.gethue.com/uploads/2015/03/hive-editor-map-1024x529.png" alt="hive-editor-map" width="1024" height="529" data-wp-pid="2450" />][3]

このリリースでは、ついにHiveServer2 APIを統一化しました。そのすべてのAPIコール（例えば、クエリのログを取得する）は、現在、アップストリームバージョンに属しています。これは、HueがHive 1.1以降の任意のバージョンとの互換性が100%になり、統合に関する多くの頭痛の種を解決します。

&nbsp;

別のメリットは、データの結果セットをはるかに速く取得する、新しい列フォーマット（カラムナフォーマット）の対応です。

&nbsp;

SSLの設定を調査している場合は、[以前のブログ記事][4]をご覧下さい 。

&nbsp;

一部のユーザーが興味を持つかもしれない。Hue 3.8が獲得したもうひとつの機能はThrift HTTPのサポートです。私たちはこの機能を[HBaseのアプリ][5]との互換性向上のために得ましたが、HiveServer2のために自由に再利用することができます

&nbsp;

[HTTP mode][6]でHiveServer2を設定する:

<pre><code class="xml">&lt;property&gt;
  &lt;name&gt;hive.server2.transport.mode&lt;/name&gt;
  &lt;value&gt;http&lt;/value&gt;
&lt;/property&gt;
</pre>

&nbsp;

正しいhive-site.xmlを[指して][7]いる場合、Hueは自動的にピックアップします。

&nbsp;

別の機能は、入力したSQLを処理するNotebook UIの開発です（現在はベータ版）。素早いプロトタイプの作成とグラフの作成ができることが分かるでしょう！

[<img class="aligncenter size-large wp-image-2451" src="https://cdn.gethue.com/uploads/2015/03/sql-notebook-1024x513.png" alt="sql-notebook" width="1024" height="513" data-wp-pid="2451" />][8]

&nbsp;

****さて、次は！****

次に登場するのは、透過的なローリングアップグレードやサーバのクラッシュに対応するためのHiveServer2の高可用性（HA）のサポートです。新しいNotebookアプリは深く開発中で、[SQLエディタ][9]と同じユーザインタフェースを共有するようになるでしょう 。

もっとユーザーが使いやすくなる、テーブル統計の視覚的な表示と、ネスト化されたタイプのオートコンプリートはもうすぐです！

&nbsp;

いつものように、コメントとフィードバックは [hue-user][10] メーリングリストや[@gethue][11]までお気軽に！

 [1]: https://hive.apache.org/
 [2]: http://impala.io/
 [3]: https://cdn.gethue.com/uploads/2015/03/hive-editor-map.png
 [4]: https://gethue.com/how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl/
 [5]: https://gethue.com/hbase-browsing-with-doas-impersonation-and-kerberos/
 [6]: https://cwiki.apache.org/confluence/display/Hive/Setting+Up+HiveServer2#SettingUpHiveServer2-RunninginHTTPmode
 [7]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [8]: https://cdn.gethue.com/uploads/2015/03/sql-notebook.png
 [9]: https://issues.cloudera.org/browse/HUE-2179
 [10]: http://groups.google.com/a/cloudera.org/group/hue-user
 [11]: https://www.google.com/url?q=https%3A%2F%2Ftwitter.com%2Fgethue&sa=D&sntz=1&usg=AFQjCNFSK0PmjkpMhs1SAQLUx4hheDzfmA