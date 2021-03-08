---
title: あなたのSearchダッシュボードをエクスポート、インポートする
author: Hue Team
type: post
date: 2015-02-26T03:49:19+00:00
url: /export-and-import-your-search-dashboards-2/
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
  - 'Hue 4、およびHUE-1660までSearchダッシュボードをインポートおよびエクスポートするための便利な方法はありませんが、これは手作業でのワークアラウンドです:'
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
  - Hue 3.8
  - Search

---
Hue 4、および[HUE-1660][1]まで[Searchダッシュボードを][2]インポートおよびエクスポートするための便利な方法はありませんが、これは手作業でのワークアラウンドです:

<pre><code class="bash">./build/env/bin/hue dumpdata search --indent 2 &lt; data.json
</pre>

続いて

<pre><code class="bash">./build/env/bin/hue loaddata data.json
</pre>

&nbsp;

これです。同じIDを持つダッシュボードはインポートされたものに更新されます！

[<img class="aligncenter size-large wp-image-2116" src="https://cdn.gethue.com/uploads/2015/02/search-dashboard-list-1024x298.png" alt="search-dashboard-list" width="1024" height="298" data-wp-pid="2116" />][3]

&nbsp;

**注**:

CMを使用している場合は、正しいデータベースを指すようにこの変数をエクスポートします。:

<pre><code class="bash">HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id
echo $HUE_CONF_DIR
export HUE_CONF_DIR</pre>

ここで<id>はhue-HUE_SERVERのための、プロセスディレクトリ内の最新のIDです。

&nbsp;

ご質問はありますか？[hue-user][4]または[@gethue][5]までお気軽にお問い合わせください！

 [1]: https://issues.cloudera.org/browse/HUE-1660
 [2]: https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr
 [3]: https://cdn.gethue.com/uploads/2015/02/search-dashboard-list.png
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
