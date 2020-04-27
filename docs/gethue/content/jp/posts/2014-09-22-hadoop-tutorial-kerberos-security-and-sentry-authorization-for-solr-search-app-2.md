---
title: Solrの検索アプリケーションのためのKerberosのセキュリティとSentryの認可
author: Hue Team
type: post
date: 2014-09-22T08:39:19+00:00
url: /hadoop-tutorial-kerberos-security-and-sentry-authorization-for-solr-search-app-2/
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
sf_remove_promo_bar:
  - 1
slide_template:
  - default
sf_custom_excerpt:
  - |
    このブログの記事では、Hueの検索アプリケーションでKerberosとSentryの使用方法を詳しく説明しています 。Kerberosのみを使用したい場合は、Sentryについての段落をスキップして下さい。
    
     
    
    Kerberos はHadoopクラスタでユーザーを認証することができます。例えば、ジョブを投入している、ファイルを一覧している、あるいは検索を実行しているのが本当にユーザー「bob」であり、「Joe」でないことを保証します。次のステップは、ユーザーが何にアクセスできるかの設定で、これは認可と呼ばれます。Sentryは、Solrのコレクション／インデックスにあるデータを、誰が参照、クエリ、追加することができるかを定義する、セキュアな方法です。
categories:
  - Enterprise
  - Search
  - Security

---
このブログの記事では、Hueの検索アプリケーションでKerberosとSentryの使用方法を詳しく説明しています 。Kerberosのみを使用したい場合は、Sentryについての段落をスキップして下さい。

&nbsp;

[Kerberos][1] はHadoopクラスタでユーザーを認証することができます。例えば、ジョブを投入している、ファイルを一覧している、あるいは検索を実行しているのが本当にユーザー「bob」であり、「Joe」でないことを保証します。次のステップは、ユーザーが何にアクセスできるかの設定で、これは[認可][2]と呼ばれます。[Sentry][3]は、Solrのコレクション／インデックスにあるデータを、誰が参照、クエリ、追加することができるかを定義する、セキュアな方法です。これは、Kerberosでアクションを実行するユーザ名を保証するようにすることのみが可能です。

&nbsp;

Hueにはインストールする準備ができているコレクションとサンプルのセット​​が付属しています。しかし、Kerberosでは、これは[ワンクリック][4]よりも少し多くの作業が必要です。

まず、あなたは[Sentryの設定がされている][5][Kerberos化されたクラスタ][6] (と[HueのSolr検索][7])を持っていることを確認して下さい。

それからコレクションを作成します。適切なSolrの環境変数がある場合、コマンドはそのまま動作するはずです。

<pre><code class="bash">cd $HUE_HOME/apps/search/examples/bin

./create_collections.sh

</pre>

&nbsp;

その後、コレクションが表示されるはずです:

<pre><code class="bash">solrctl instancedir --list
jobs_demo
log_analytics_demo
twitter_demo
yelp_demo
</pre>

&nbsp;

次のステップは、Solrのコアを作成することです。シンプルに保つために、私たちは1つのコレクションを使用してtwitterのデモを行います。コアを作成する際に、

<pre><code class="bash">sudo -u systest solrctl collection --create twitter_demo -s 1</pre>

Sentryを使用している場合、あなたはおそらく、このエラーを最初にご覧になるでしょう:

<pre><code class="bash">Error: A call to SolrCloud WEB APIs failed: HTTP/1.1 401 Unauthorized
Server: Apache-Coyote/1.1
WWW-Authenticate: Negotiate
Set-Cookie: hadoop.auth=; Version=1; Path=/; Expires=Thu, 01-Jan-1970 00:00:00 GMT; HttpOnly
Content-Type: text/html;charset=utf-8
Content-Length: 997
Date: Thu, 11 Sep 2014 16:32:17 GMT&lt;/pre&gt;
&lt;pre&gt;HTTP/1.1 401 Unauthorized
Server: Apache-Coyote/1.1
WWW-Authenticate: Negotiate YGwGCSqGSIb3EgECAgIAb10wW6ADAgEFoQMCAQ+iTzBNoAMCARCiRgRE62zOpPwr+KLoFKdUX2I6FtbN0DyxSA5a8n4BSZRJMTf413TEXzJbVh3/G7jWiMasIIzeETrd0Bv8suBsuKS/HdqG068=
Set-Cookie: hadoop.auth="u=systest&p=systest@ENT.CLOUDERA.COM&t=kerberos&e=1410489137684&s=qAkcQr4ZPBkn5Ewg/Ugz/CqgLkU="; Version=1; Path=/; Expires=Fri, 12-Sep-2014 02:32:17 GMT; HttpOnly
Content-Type: application/xml;charset=UTF-8
Transfer-Encoding: chunked
Date: Thu, 11 Sep 2014 16:32:17 GMT

&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;response&gt;
&lt;lst name="responseHeader"&gt;
&lt;int name="status"&gt;
401&lt;/int&gt;
&lt;int name="QTime"&gt;
18&lt;/int&gt;
&lt;/lst&gt;
&lt;lst name="error"&gt;
&lt;str name="msg"&gt;
org.apache.sentry.binding.solr.authz.SentrySolrAuthorizationException: User systest does not have privileges for admin&lt;/str&gt;
&lt;int name="code"&gt;
401&lt;/int&gt;
&lt;/lst&gt;

</pre>

&nbsp;

これは、デフォルトでは「systest」ユーザーがコアを作成する権限を持っていないためです。「systestの」は「admin」のUnix / LDAPグループに属しており、「admin」という名前の権限が含まれるSentryグループを作成する必要があります。私たちの「systest」ユーザーは、この役割を含むグループに属している必要があります。

&nbsp;

これには更新を行う必要があります:

<pre><code class="bash">/user/solr/sentry/sentry-provider.ini</pre>

&nbsp;

これに似たもので更新します：

<pre><code class="bash">[groups]
admin = eng_role
analyst = read_only_role

[roles]
eng_role = collection = twitter_demo, collection = admin
read_only_role = collection = twitter_demo -&gt; action = query
update_only_role = collection = twitter_demo -&gt; action = update
</pre>

&nbsp;

「systest」はLDAPの「admin」グループに属しています。 「admin」は「admin」権限を持つ「eng\_role」の役割が割り当てられています。通常のアナリストのユーザーは、Sentryの「read\_only」の役割とTwitterの収集のための「query」の許可を含む、LDAPの「analyst」グループに属しています。これが利用可能なの[権限][8]の一覧です。

&nbsp;

**備考**

今度のHue3.7には、sentry-provider.iniを忘れることができ、Web UIからこれらを設定できる新しいSentryアプリがあります。また、SolrのSentryのサポートのAPIが利用可能になるとすぐに、私たちはHueに統合しています。

&nbsp;

次は、コアを作成し、いくつかのデータをアップロードするための時間です。Kerberosで動作させるようにするために[post.sh][9]コマンドを更新します。

以下の「curl 」を置き換えます:

<pre><code class="bash">curl --negotiate -u: foo:bar</pre>

&nbsp;

URLに実際のホスト名を使用してください：

<pre><code class="bash">URL=http://hue-c5-sentry.ent.cloudera.com:8983/solr</pre>

&nbsp;

テストを行う簡単な方法は、インデキシングコマンドを実行することです：

<pre><code class="bash">sudo -u systest curl --negotiate -u: foo:bar http://hue-c5-sentry.ent.cloudera.com:8983/twitter_demo/update --data-binary @../collections/solr_configs_twitter_demo/index_data.csv -H 'Content-type:text/csv'</pre>

&nbsp;

これです！そのデータのコレクションは、SolrとHueに表示されます。そのグループに応じて、ユーザーはコレクションを変更することはできる、またはすることができません。

[<img class="aligncenter size-large wp-image-1634" src="https://cdn.gethue.com/uploads/2014/09/hue-collections-1024x488.png" alt="hue-collections" width="1024" height="488" data-wp-pid="1634" />][10]

&nbsp;

これであなたの企業、組織では、きめの細かいセキュリティを備えた検索アプリケーションの探索機能を活用することができます！次のバージョンでは、フィールドレベルでのセキュリティと、それを構成するための素晴らしいUIが搭載されるでしょう（もうsentry-provider.iniは不要です :)。

&nbsp;

いつものように、コメントとフィードバックは[hue-user][11] メーリングリストや[@gethue][12]までお気軽に！

 [1]: http://ja.wikipedia.org/wiki/%E3%82%B1%E3%83%AB%E3%83%99%E3%83%AD%E3%82%B9%E8%AA%8D%E8%A8%BC
 [2]: http://ja.wikipedia.org/wiki/%E8%AA%8D%E5%8F%AF_(%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3)
 [3]: https://sentry.incubator.apache.org/
 [4]: https://gethue.com/tutorial-live-demo-of-search-on-hadoop/
 [5]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM4Ent/latest/Cloudera-Manager-Managing-Clusters/cmmc_sentry_search_config.html
 [6]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Security-Guide/CDH5-Security-Guide.html
 [7]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Security-Guide/cdh5sg_search_security.html#concept_jrk_lzc_fm_unique_2
 [8]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-User-Guide/csug_sentry.html#concept_wc2_yhp_wk_unique_1
 [9]: https://github.com/cloudera/hue/blob/master/apps/search/examples/bin/post.sh
 [10]: https://cdn.gethue.com/uploads/2014/09/hue-collections.png
 [11]: http://groups.google.com/a/cloudera.org/group/hue-user
 [12]: https://twitter.com/gethue