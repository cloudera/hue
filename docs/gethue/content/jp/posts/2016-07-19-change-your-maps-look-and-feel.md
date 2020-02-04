---
title: 地図のルック＆フィールを変更する
author: Hue Team
type: post
date: 2016-07-19T00:00:17+00:00
url: /change-your-maps-look-and-feel/
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
sf_custom_excerpt:
  - 2つの特別な変数をHueの設定に指定するだけで、Hueの地図のルック＆フィールを変更することができることをご存知でしたか？
categories:
  - Hue 3.11
  - SDK
  - SQL

---
2つの特別な変数を<a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L114" target="_blank">Hueの設定</a>に指定するだけで、Hueの地図のルック＆フィールを変更することができることをご存知でしたか？

[<img class="aligncenter size-large wp-image-4229" src="https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.15.19-1024x590.jpg" alt="Screenshot 2016-07-18 21.15.19" width="1024" height="590" data-wp-pid="4229" />][1]

上記はHueの地図のデフォルトのスタイルです。私たちは描画にオープンソースのライブラリである<a href="http://leafletjs.com/" target="_blank">Leaflet</a>を使用しています。

LeafletはHueで使用することができる、地図プロバイダのリストを一緒にまとめる素晴らしい作業も行いました: <a href="https://leaflet-extras.github.io/leaflet-providers/preview/" target="_blank">https://leaflet-extras.github.io/leaflet-providers/preview/</a>

[<img class="aligncenter size-large wp-image-4232" src="https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.23.35-1024x660.jpg" alt="Screenshot 2016-07-18 21.23.35" width="1024" height="660" data-wp-pid="4232" />][2]

Esriを表示してみましょう。Hueでの衛星画像です！

微調整する必要があるプロパティは`leaflet_tile_layer`と`leaflet_tile_layer_attribution` で、hue.iniファイルで設定できます：

<pre><code class="bash">[desktop]
leaflet_tile_layer=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
leaflet_tile_layer_attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
</pre>

値はLeafletプロバイダのデモで扱っているものとまったく同じです。
  
Hueでの最新のセキュリティの改善により、`server.arcgisonline.com`同様にタイルドメインをホワイトリストに登録して`*.tile.osm.org`の代わりに置く必要があります。

<pre><code class="bash">[desktop]
secure_content_security_policy="script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google-analytics.com *.doubleclick.net *.mathjax.org data:;img-src 'self' *.google-analytics.com *.doubleclick.net server.arcgisonline.com data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'none';object-src 'none'"
</pre>

驚くべきことに、Hueを再起動すると地図を使用するすべてのアプリが衛星画像になっています！

[<img class="aligncenter size-large wp-image-4234" src="https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.26.53-1024x575.jpg" alt="Screenshot 2016-07-18 21.26.53" width="1024" height="575" data-wp-pid="4234" />][3]

いつものように、コメントとフィードバックは [hue-user][4] メーリングリストや[@gethue][5]までお気軽に！

 [1]: https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.15.19.jpg
 [2]: https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.23.35.jpg
 [3]: https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.26.53.jpg
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue