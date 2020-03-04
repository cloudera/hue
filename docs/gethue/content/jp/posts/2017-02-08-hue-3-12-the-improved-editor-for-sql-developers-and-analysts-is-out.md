---
title: SQL開発者やアナリスト用のエディタが改善された Hue3.12 が公開されました！
author: Hue Team
type: post
date: 2017-02-08T10:16:53+00:00
url: /hue-3-12-the-improved-editor-for-sql-developers-and-analysts-is-out/
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
categories:
  - Hue 3.12
  - Release
  - SQL

---
ビッグデータエクスプローラの皆さん、こんにちは。

&nbsp;

Hueチームは全てのコントリビューターに感謝し、Hue 3.12のリリースを嬉しく思います！  [<img class="aligncenter size-full wp-image-2988" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo (copy)" width="85" height="63" data-wp-pid="2988" />][1]

この最新のHueのアップデートは、SQL開発者とアナリスト向けのインテリジェントなエディタとセキュリティに重点を置いていました。[3.11][2]には[1570以上のコミット][3]が入りました！tarball版のリリースを入手して試してみてください！

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="arボールのリリースをクリックしてダウンロード" href="https://dl.dropboxusercontent.com/u/730827/hue/releases/3.12.0/hue-3.12.0.tgz" target="_blank"><br /> <span class="text">Download</span><br /> </a>
</p>

より詳細なブログへのリンクがあります。全ての変更については [リリースノート][4] を参照してください。また、 <span style="font-weight:400">手っ取り早く試すには </span>[<span style="font-weight:400">demo.gethue.com</span>][5]<span style="font-weight:400">を開いてみて下さい</span>

&nbsp;

# **SQLの改善**

<span style="font-weight: 400;">Hueのエディタは、下記のような大きな改善点を得ています：</span>

## <span style="font-weight: 400;">行数</span>

<span style="font-weight: 400;">返却された行数が表示されるので、データセットのサイズをすばやく確認できます。データベースエンジンが行数を提供しない場合、Hueは行数を推定し、プラス記号（100+など）を追加します。</span>

[<img class="aligncenter size-full wp-image-4583" src="https://cdn.gethue.com/uploads/2016/12/result-count.png" alt="" width="757" height="448" data-wp-pid="4583" />][6]

## <span style="font-weight: 400;">サンプルのポップアップ</span>

<span style="font-weight: 400;">このポップアップを使用すると、データのサンプルと、データベース、テーブル、列に関するその他の統計情報をすばやく表示できます。SQLアシストから、あるいは任意のSQLオブジェクト（テーブル、列、関数&#8230;）を右クリックしてポップアップを開くことができます。このリリースでは、ポップアップはより早く開き、データがキャッシュされます。</span>

[<img class="aligncenter size-full wp-image-4662" src="https://cdn.gethue.com/uploads/2016/12/right_click_editor_assist-1.png" alt="" width="658" height="544" data-wp-pid="4662" />][7]

<span style="font-weight: 400;">フッターは、メタストアのページへまたはテーブルアシスト内のテーブルへの直接リンクを提供します。</span>

&nbsp;

## <span style="font-weight: 400;">SQLアシスト</span>

<span style="font-weight: 400;">アイテムのレンダリングが書き直され、最適化されました。何千もの列を持つデータベースでは、どのような遅れも経験すべきではありません。</span>

[<img class="aligncenter size-full wp-image-4585" src="https://cdn.gethue.com/uploads/2016/12/dragdrop_from_asssist.png" alt="" width="692" height="304" data-wp-pid="4585" />][8]

## <span style="font-weight: 400;">SQLフォーマッタ</span>

<span style="font-weight: 400;">SQLフォーマッタには、ワンクリックできれいに見える新しいスマートなアルゴリズムが用意されています！</span>

## <span style="font-weight: 400;">タイムラインとピボットグラフ</span>

<span style="font-weight: 400;">これらのビジュアライゼーションは、時系列データをプロットする場合や、行のサブセットが同じ属性を持ち、それらを一緒に積み重ねる場合に便利です。</span>

[<img class="aligncenter size-large wp-image-4588" src="https://cdn.gethue.com/uploads/2016/12/sql_timeline_chart-1024x351.png" alt="" width="1024" height="351" data-wp-pid="4588" />][9]

<span style="font-weight: 400;">タイムライン</span>

[<img class="aligncenter size-large wp-image-4639" src="https://cdn.gethue.com/uploads/2016/12/pivot_graph-1024x275.png" alt="" width="1024" height="275" data-wp-pid="4639" />][10]

 <span style="font-weight: 400;">ピボット </span>

## <span style="font-weight: 400;">外部テーブルの作成</span>

<span style="font-weight: 400;">S3用に改善した太陽により、HDFSまたはS3に直接外部テーブルを作成する機会を導入しました。</span>

&nbsp;

SQLの改善について[<span style="font-weight:400">詳しく読む</span>][11]<span style="font-weight:400"></span></span>

# 

# **自動化されたS3の設定**

<span style="font-weight: 400;">ClouderaのManagerを使用してS3が設定されている場合、HueはS3の資格情報を自動的に継承します。</span>

[<img class="aligncenter size-full wp-image-4669" src="https://cdn.gethue.com/uploads/2017/02/s3_connector.png" alt="" width="172" height="65" data-wp-pid="4669" />][12]

<span style="font-weight:400">通常のユーザーが自動的に</span> [<span style="font-weight:400">S3ブラウザとオートコンプリート</span>][2] <span style="font-weight:400">にアクセスすることはありません。それらはグループの1つに追加されたHueユーザー管理で「ファイルブラウザのS3権限 (File Browser S3 permission)」を持っている必要があります。</span>

&nbsp;

<span style="font-weight:400">S3の設定について</span>[<span style="font-weight:400">詳しく読む。</span>][13]<span style="font-weight:400"></span>

&nbsp;

# **新しいセキュリティの改善**

<span style="font-weight: 400;">管理者が安全なHueインストールを強制して管理するのに役立つ多くのセキュリティオプションが追加されました。</span>

### 固定の任意のホストヘッダの受け入れ

Hueは任意のホストヘッダ受け入れを修正しました。これで、Hueサーバが提供できるホスト/ドメイン名を設定できます。
  
allowed_hosts=”host.domain,host2.domain,host3.domain”

<pre><code class="bash">[desktop]
allowed_hosts=&amp;amp;quot;*.domain&amp;amp;quot;
# your own fqdn example: allowed_hosts=&amp;amp;quot;*.hadoop.cloudera.com&amp;amp;quot;
# or specific example: allowed_hosts=&amp;amp;quot;hue1.hadoop.cloudera.com,hue2.hadoop.cloudera.com&amp;amp;quot;
</pre>

<span style="color: #ff0000;"><strong>注</strong></span> ：「Bafd Request（400）」エラー：[AWSクラスタでHueをホストする場合][14]、ネットワークの外部クライアントがHueにアクセスできるようにするには、値を「*」設定する必要があります。

## <span style="font-weight: 400;">HttpOnlyフラグでの固定セッションIDとcsrftoken</span>

<span style="font-weight: 400;">HttpOnlyフラグがHTTPレスポンスヘッダに含まれている場合、クライアント側のスクリプトを使用してCookieにアクセスすることはできません。従って、ブラウザはCookieを第三者に公開しません。クロスサイトスクリプティングのリスクを軽減するため、この属性を持つCookieはHTTP専用Cookieと呼ばれます。 HTTP専用Cookieに含まれる情報は、ハッカーや悪意のあるWebサイトに漏洩する可能性が低くなります。</span>

## <span style="font-weight: 400;"><code>hive.server2.thrift.sasl.qop=”auth-conf”</code>のためのSASLのサポート</span>

<span style="font-weight: 400;">SASLの機構は、認証が成功した後、通信チャネルの完全性とプライバシー保護をサポートしています。 </span>

<span style="font-weight: 400;">Thrift SASLライブラリ<span style="font-weight:400">では、sasl_max_buffer</span></span> <span style="font-weight:400"><span style="font-weight:400">サポート</span>は既に実装されています。</span> <span style="font-weight:400">hue.ini</span> <span style="font-weight:400">の</span> <span style="font-weight:400">sasl_max_buffer <span style="font-weight:400"></span>は</span> <span style="font-weight:400"></span> <span style="font-weight:400"><code>hive.server2.thrift.sasl.qop="auth-conf"&lt;code></code></code></span>のサポートを可能にする、より大きく設定可能なバッファサイズを提供します。</span>

<pre><code class="bash">[desktop]
# This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication (default 2 MB).
sasl_max_buffer=2 * 1024 * 1024
</pre>

## <span style="font-weight: 400;">HueのRequest HTTPプールの紹介</span>

<span style="font-weight: 400;"Request Sessionオブジェクトは、要求間の特定のパラメータの永続性を可能にします。また、セッションインスタンスから作成されたすべてのリクエストにCookieを永続化し、urllib3の接続プールを使用します。同じ host:port に対して複数のリクエストを行っていますが、この変更により、基本的なTCP接続が再利用されるため、パフォーマンスが大幅に向上します。</span>

<pre><code class="python">CACHE_SESSION = requests.Session()
CACHE_SESSION.mount('http://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))
CACHE_SESSION.mount('https://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))
</pre>

## Content-Security-Policy: ヘッダ

新しいContent-Security-Policy HTTPレスポンスヘッダーは、最新のブラウザーでクロスサイトスクリプティングのリスクを軽減するのに役立ちます。これは、HTTPヘッダーを介してどの動的リソースがロードできるかを宣言することによって実現されます。（詳しくは <https://content-security-policy.com/> をご覧ください）

<pre><code class="bash">[desktop]
secure_content_security_policy=&amp;amp;quot;script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google-analytics.com *.doubleclick.net *.mathjax.org data:;img-src 'self' *.google-analytics.com *.doubleclick.net http://*.tile.osm.org *.tile.osm.org *.gstatic.com data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'self' data:;object-src 'none'&amp;amp;quot;
#In HUE 3.11 and higher it is enabled by default.
</pre>

&nbsp;

セキュリティの向上については[ここ][15]と[ここ][16]をご覧ください 。

&nbsp;

# **Oozieの改善**

## <span style="font-weight: 400;">電子メール通知</span>

<span style="font-weight: 400;">ワークフローの実行が完了した後、電子メール通知を受信するのが容易になります。ワークフローサブミットのポップアップに「完了メールを送信 (Send completion email」のチェックボックスが表示されます。</span>

[<img class="aligncenter wp-image-4595" src="https://cdn.gethue.com/uploads/2016/12/send-email-checkbox.png" alt="" width="418" height="150" data-wp-pid="4595" />][17]

## <span style="font-weight: 400;">拡張ダッシュボードのフィルタリング</span>

<span style="font-weight: 400;">テキストフィールドに入力を開始すると、テキストと名前または投稿者の一部が一致したジョブのリストが取得できます。下記の画像では、テキスト<span style="font-weight:400">SH</span></span> <span style="font-weight:400">が</span> {2すべての4つのジョブの名前と部分的に一致 することがわかります</span> <span style="font-weight:400">。フィルタは現在のページにあるものだけでなく、すべてのジョブに適用されることに注意してください。</span>

[<img class="aligncenter size-large wp-image-4603" src="https://cdn.gethue.com/uploads/2016/12/name-search-1024x524.png" alt="" width="1024" height="524" data-wp-pid="4603" />][18]

<span style="font-weight: 400;">サブミットされた何千ものジョブの中から1つのジョブを見つけるには、完全なIDを入力する必要があります。</span>

&nbsp;

<span style="font-weight: 400;">Oozieの改善点<a href="https://gethue.com/oozie-improvements-in-3-12-with-email-notifications-and-extended-dashboard-filtering/"><span style="font-weight:400">こちら</span></a>については<span style="font-weight:400">をご覧ください<span style="font-weight: 400;">.</span></p> 

<p>
  &nbsp;
</p>

<h2>
  チームリトリート
</h2>

<p>
  <a href="https://cdn.gethue.com/uploads/2016/12/IMG_5609.jpg"><img class="aligncenter wp-image-4551" src="https://cdn.gethue.com/uploads/2016/12/IMG_5609-1024x768.jpg" alt="" width="524" height="393" data-wp-pid="4551" /></a> <a href="https://cdn.gethue.com/uploads/2016/10/IMG_5290.jpg"><img class="aligncenter wp-image-4529" src="https://cdn.gethue.com/uploads/2016/10/IMG_5290-1024x768.jpg" alt="" width="520" height="390" data-wp-pid="4529" /></a>
</p>

<ul>
  <li>
    <a href="https://gethue.com/team-retreat-in-malaysia-an">マレーシア、カンボジア</a>
  </li>
  <li>
    <a href="https://gethue.com/team-retreat-in-riga/">リガ、ラトビアの首都</a>
  </li>
</ul>

<p>
  &nbsp;
</p>

<h2>
  <b>さて、その次は!</b>
</h2>

<p>
  次のリリースでは、データのSQL版とデータの発見機能が改善されます。Hue 4は「ビッグデータのためのExcel」に相当する目標を達成するために、現実のものとなるでしょう。現在のアプリケーションは<a href="https://gethue.com/sql-editor/">新しいエディタ</a>に統合されており、Hue全体がオンプレミスまたはクラウドのHadoopで、最高のデータアナリティクスのユーザーエクスペリエンスを提供する単一のアプリケーションになります。
</p>

<p>
  &nbsp;
</p>

<p>
  さらにその先へ！
</p>

<p>
  &nbsp;
</p>

<p>
  いつものように、すべてのプロジェクトの貢献者とフィードバックを送信してくれる方、<a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a> メーリングリストまたは<a href="https://twitter.com/gethue">@gethue</a>に参加してくれる方々に感謝しています！
</p>

<p>
  &nbsp;
</p>

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
 [3]: http://cloudera.github.io/hue/docs-3.12.0/release-notes/release-notes-3.12.0.html#_list_of_1570_commits
 [4]: http://cloudera.github.io/hue/docs-3.12.0/release-notes/release-notes-3.12.0.html
 [5]: http://demo.gethue.com/
 [6]: https://cdn.gethue.com/uploads/2016/12/result-count.png
 [7]: https://cdn.gethue.com/uploads/2016/12/right_click_editor_assist-1.png
 [8]: https://cdn.gethue.com/uploads/2016/12/dragdrop_from_asssist.png
 [9]: https://cdn.gethue.com/uploads/2016/12/sql_timeline_chart.png
 [10]: https://cdn.gethue.com/uploads/2016/12/pivot_graph.png
 [11]: https://gethue.com/sql-improvements-with-row-counts-sample-popup-and-more/
 [12]: https://cdn.gethue.com/uploads/2017/02/s3_connector.png
 [13]: https://www.cloudera.com/documentation/enterprise/latest/topics/hue_use_s3_enable.html#concept_p2v_1yl_gy
 [14]: https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/
 [15]: https://gethue.com/hue-security-improvements/
 [16]: https://gethue.com/security-improvements-http-only-flag-sasl-qop-and-more/
 [17]: https://cdn.gethue.com/uploads/2016/12/send-email-checkbox.png
 [18]: https://cdn.gethue.com/uploads/2016/12/name-search.png