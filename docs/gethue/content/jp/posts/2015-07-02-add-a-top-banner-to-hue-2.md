---
title: Hueにトップバナーを追加！
author: Hue Team
type: post
date: 2015-07-02T04:50:56+00:00
url: /add-a-top-banner-to-hue-2/
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
  - 私たちはこの記事で 、あなたのクラスタ内のHueをどのように設定するかについて見てきました。しかし、あなたはHueのインストールで表示されるトップバナーを作ることができるプロパティがあることをご存知でしたか？
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
  - Programming
  - SDK

---
私たちは<a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank">この記事</a>で 、あなたのクラスタ内のHueをどのように設定するかについて見てきました。しかし、あなたはHueのインストールで表示されるトップバナーを作ることができるプロパティがあることをご存知でしたか？

[<img class="aligncenter size-large wp-image-2363" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12-1024x610.png" alt="Screenshot 2015-03-23 16.33.12" width="1024" height="610" data-wp-pid="2363" />][1] This is quite useful if youユーザーに免責事項を表示したり、テスト環境や本番環境を明確にしたり、またはそこにいくつかの動的な情報を表示したい場合には非常に便利です。あなたが <a href="https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/" target="_blank">Cloudera Manager</a>を使用しているか否かにより、この機能を使用するには安全バルブ(Safety valve)を追加するか.iniファイルを編集するどちらかの必要があります。設定を変更する方法の詳細については <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank">こちらをご覧ください</a> 。iniファイルのdesktop/customセクションに、banner\_top\_htmlプロパティを見つけることができるでしょう:

<pre><code class="bash">[desktop]
[[custom]]
# Top banner HTML code
banner_top_html=
</pre>

それからいくつかのHTML/CSSおよびJavascriptのコードでさえ、あなたが好むようなカスタマイズを書くだけです。これには高さの制約（30px）があることにご注意ください。。たとえば、この記事の冒頭の画像のように、オレンジ色の背景に白色のメッセージを書くためには、このように記述できます:

<!--email_off-->

<pre><code class="bash">[desktop]
[[custom]]
# Top banner HTML code
banner_top_html='&lt;/pre&gt;
&lt;div&gt;&lt;i class=&quot;&amp;quot;fa&quot;&gt;&lt;/i&gt; This is the test environment for Acme, Inc. - For any problem &lt;a href=&quot;&amp;quot;mailto:roadrunner@acme.com&amp;quot;&quot;&gt;roadrunner@acme.com&lt;/a&gt;&lt;/div&gt;
&lt;pre&gt;'
</pre>

&nbsp;

あるいは、実行ティッカーを表示するために非常に古いHTMLタグを使用することさえもできます！

<pre><code class="bash">[desktop]
[[custom]]
# Top banner HTML code
banner_top_html='Welcome to the test environment.'
</pre>

[<img class="aligncenter size-large wp-image-2365" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-18.56.32-1024x610.png" alt="Screenshot 2015-03-23 18.56.32" width="1024" height="610" data-wp-pid="2365" />][2]
  
そして、Hueの一番上にいくつかのリアルタイム情報を表示するには？例として、最新の<a href="https://www.nasa.gov/mission_pages/station/main/" target="_blank">ISS</a>の位置をすべてのページのバナーで更新するように変更します（<a href="http://open-notify.org/" target="_blank">Open Notify</a>のおかげです）

<pre><code class="bash">[desktop]
[[custom]]&lt;/pre&gt;
&lt;div class="line number4 index3 alt1"&gt;&lt;/div&gt;
&lt;div class="line number4 index3 alt1"&gt;&lt;code class="bash plain"&gt;banner_top_html='&lt;script&gt;&lt;/code&gt;&lt;code class="bash plain"&gt;//&lt;/code&gt; &lt;code class="bash plain"&gt;&lt;![CDATA[&lt;/code&gt;&lt;/div&gt;
&lt;div class="line number5 index4 alt2"&gt;&lt;code class="bash plain"&gt;$(document).ready(&lt;/code&gt;&lt;code class="bash keyword"&gt;function&lt;/code&gt;&lt;code class="bash plain"&gt;(){ $.getJSON(&quot;http:&lt;/code&gt;&lt;code class="bash plain"&gt;//api&lt;/code&gt;&lt;code class="bash plain"&gt;.&lt;/code&gt;&lt;code class="bash functions"&gt;open&lt;/code&gt;&lt;code class="bash plain"&gt;-notify.org&lt;/code&gt;&lt;code class="bash plain"&gt;/iss-now&lt;/code&gt;&lt;code class="bash plain"&gt;.json?callback=?&quot;, &lt;/code&gt;&lt;code class="bash keyword"&gt;function&lt;/code&gt;&lt;code class="bash plain"&gt;(data){ $(&quot;&lt;/code&gt;&lt;code class="bash comments"&gt;#isspos&quot;).html(&quot;LAT: &quot;+data.iss_position.latitude+&quot;, LNG: &quot;+data.iss_position.longitude); }); })&lt;/code&gt;&lt;/div&gt;
&lt;div class="line number6 index5 alt1"&gt;&lt;code class="bash plain"&gt;//&lt;/code&gt; &lt;code class="bash plain"&gt;]]&gt;&lt;&lt;/code&gt;&lt;code class="bash plain"&gt;/script&lt;/code&gt;&lt;code class="bash plain"&gt;&gt;&lt;&lt;/code&gt;&lt;code class="bash plain"&gt;/pre&lt;/code&gt;&lt;code class="bash plain"&gt;&gt;&lt;/code&gt;&lt;/div&gt;
&lt;div class="line number7 index6 alt2"&gt;&lt;code class="bash plain"&gt;&lt;div&gt;The current ISS position is &lt;span &lt;/code&gt;&lt;code class="bash functions"&gt;id&lt;/code&gt;&lt;code class="bash plain"&gt;=&lt;/code&gt;&lt;code class="bash string"&gt;"&quot;isspos&quot;"&lt;/code&gt;&lt;code class="bash plain"&gt;&gt;&lt;&lt;/code&gt;&lt;code class="bash plain"&gt;/span&lt;/code&gt;&lt;code class="bash plain"&gt;&gt;&lt;&lt;/code&gt;&lt;code class="bash plain"&gt;/div&lt;/code&gt;&lt;code class="bash plain"&gt;&gt;&lt;/code&gt;&lt;/div&gt;
&lt;div class="line number8 index7 alt1"&gt;&lt;code class="bash plain"&gt;&lt;pre&gt;'&lt;/code&gt;&lt;/div&gt;
&lt;pre&gt;</pre>

[<img class="aligncenter size-large wp-image-2364" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.57.33-1024x610.png" alt="Screenshot 2015-03-23 16.57.33" width="1024" height="610" data-wp-pid="2364" />][3]かなりクールでしょう？そう、何か便利なものを作成するのはあなたの番です！いつものように、コメントとフィードバックは [hue-user][4] メーリングリストや[@gethue][5]までお気軽に！

 [1]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12.png
 [2]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-18.56.32.png
 [3]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.57.33.png
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue