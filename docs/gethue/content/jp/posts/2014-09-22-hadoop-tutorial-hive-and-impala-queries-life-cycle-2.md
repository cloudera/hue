---
title: HiveとImpalaクエリのライフサイクル
author: Hue Team
type: post
date: 2014-09-22T09:01:22+00:00
url: /hadoop-tutorial-hive-and-impala-queries-life-cycle-2/
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
sf_author_info:
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
slide_template:
  - default
sf_custom_excerpt:
  - |
    HiveとImpalaのSQLエディタによって、Hueはよく使用されるようになっています:

    しかし、クエリの結果はどうなるのでしょうか？それらはどのくらい保持されているのでしょうか？それらはなぜ時々消えているのでしょうか？なぜ一部のImpalaのクエリは、それらが完了した場合でも、まだ「実行中」なのでしょうか？
categories:
  - Hive
  - Impala

---
HiveとImpalaの[SQLエディタ][1]によって、Hueはよく使用されるようになっています:

[<img class="aligncenter size-large wp-image-1636" src="https://cdn.gethue.com/uploads/2014/09/impala-ui-1024x568.png" alt="impala-ui" width="1024" height="568" data-wp-pid="1636" />][2]

しかし、クエリの結果はどうなるのでしょうか？それらはどのくらい保持されているのでしょうか？それらはなぜ時々消えているのでしょうか？なぜ一部のImpalaのクエリは、それらが完了した場合でも、まだ「実行中」なのでしょうか？

各クエリでは、ImpalaやHiveServer2のいくつかのリソースを使用しています。ユーザが多くのクエリを投入すると、何も起こらない場合にはサーバを起動してクラッシュします。多くの改善が行われたHue 3 とCDH4.6のHueでは、自動的にすべてのメタデータクエリをクローズするようになりました。これらは微調整することができる最新の設定です:

# Impala

Hueは、ユーザが結果ページから移動する際にクエリをクローズしようとします（クエリは一般的に高速なので、それらをすぐにクローズするのはOKです）。しかし、ユーザーがクエリの結果を確認しに戻ってこなかったり、ページをクローズしなかったりした場合、クエリは保持されたままになります。（[HUE-2251][3]で）Hue 3.7とC5.2から、Impalaは[query\_timeout\_s][4]プロパティで10分以上アイドルになると、自動的にクエリが期限切れになります。

<pre><code class="bash">[impala]
  # If QUERY_TIMEOUT_S &gt; 0, the query will be timed out (i.e. cancelled) if Impala does not do any work (compute or send back results) for that query within QUERY_TIMEOUT_S seconds.
  query_timeout_s=600
</pre>

このバージョンまでの唯一の代替回避策は、すべてのクエリをクローズするためにHue（またはImpala）を再起動することです。

# Hive

（いくつかのクエリには数時間処理がかかることがあるように）Hueは、デフォルトではHiveのクエリをクローズすることはありません。クエリの量が少ない（例えば、一日に数百未満）、かつ毎週HiveServer2を再起動する場合にはおそらく影響ありません。Impalaと同じ振る舞い（およびユーザーがページを離れたときに、クエリをクローズする）を得るには、hue.iniでオンに切り替えます：

<pre><code class="bash">[beeswax]
  # Hue will try to close the Hive query when the user leaves the editor page.
  #This will free all the query resources in HiveServer2, but also make its results inaccessible.
  close_queries=true
</pre>

CDH5と（HiveServer2のある）CDH4.6から、Hueにはいくつかのclose\_queryとclose\_sessionコマンドが追加されました。

<pre><code class="bash">build/env/bin/hue close_queries --help

Usage: build/env/bin/hue close_queries [options] &lt;age_in_days&gt;  (default is 7)

</pre>

7日以上古い実行されていないクエリをクローズします。<all>が指定されている場合は、いかなる種類のものもクローズします。Cloudera Managerを使用してそれらを実行するには、次の2つの環境変数をエクスポートしてください：

<pre><code class="bash">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'`"

./build/env/bin/hue close_queries 0
Closing (all=False) HiveServer2 queries older than 0 days...
1 queries closed.

./build/env/bin/hue close_sessions 0 hive
Closing (all=False) HiveServer2 sessions older than 0 days...
1 sessions closed.

</pre>

その後crontabにこのコマンドを追加して、N日以上経過したクエリを期限切れにすることができます。

**備考**

Kerberosを使用する際にも必要です:

<pre><code class="bash">export HIVE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'`/hive-conf"</pre>

（Hive 0.14またはC5.2で利用可能になる）[HIVE-5799][5]の「クリーナー」ソリューションがあります。Impalaのように、これでHiveServer2は自動的にクエリを期限切れにすることができます。hive-site.xmlを少し編集します:

<pre><code class="xml">&lt;property&gt;
  &lt;name&gt;hive.server2.session.check.interval&lt;/name&gt;
  &lt;value&gt;3000&lt;/value&gt;
  &lt;description&gt;The check interval for session/operation timeout, which can be disabled by setting to zero or negative value.&lt;/description&gt;
&lt;/property&gt;

&lt;property&gt;
  &lt;name&gt;hive.server2.idle.session.timeout&lt;/name&gt;
  &lt;value&gt;0&lt;/value&gt;
  &lt;description&gt;Session will be closed when it's not accessed for this duration, which can be disabled by setting to zero or negative value.&lt;/description&gt;
&lt;/property&gt;

&lt;property&gt;
  &lt;name&gt;hive.server2.idle.operation.timeout&lt;/name&gt;
  &lt;value&gt;0&lt;/value&gt;
  &lt;description&gt;Operation will be closed when it's not accessed for this duration of time, which can be disabled by setting to zero value. With positive value, it's checked for operations in terminal state only (FINISHED, CANCELED, CLOSED, ERROR). With negative value, it's checked for all of the operations regardless of state.&lt;/description&gt;
&lt;/property&gt;
</pre>

**備考**

これはHiveのために推奨されるソリューションです。ユーザーが長く結果を保持したいと思う場合、CREATE TABLE AS SELECT&#8230; またはHueで結果をエクスポートすることができます。

# 総括

リソースが無限に増えていく必要がないので、クエリサーバーは、これらの変更によりはるかに安定してきています。トレードオフの一つは、ユーザーが一定時間後にクエリの結果を失うことになるということです。経験をより良いものにするために、自動的に結果セットのN行をダウンロードし、より長くそれらを保つように、いくつかのアイデアでが調査されています。

いつものように、コメントとフィードバックは[hue-user][6] メーリングリストや[@gethue][7]までお気軽に！

 [1]: https://gethue.com/hadoop-tutorial-new-impala-and-hive-editors/
 [2]: https://cdn.gethue.com/uploads/2014/09/impala-ui.png
 [3]: https://issues.cloudera.org/browse/HUE-2251
 [4]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L818
 [5]: https://issues.apache.org/jira/browse/HIVE-5799
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
