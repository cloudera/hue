---
title: Mustacheを使用して検索のHTMLの出力を改善する！
author: Hue Team
type: post
date: 2015-08-11T02:33:56+00:00
url: /enhance-search-results-2/
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
  - HueのSearch(検索)アプリはどんどんよくなっています ！Hueの次のリリース（または既にGithubのマスター にある）では、あなたは、HueのMustacheのバージョンに追加機能を加えることができるようになり、HTMLの表示で直接関数を呼び出すことができます。どのように使用するのかを見てみましょう！
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
  - Hue 3.9
  - Programming
  - Search
  - Tutorial

---
HueのSearch(検索)アプリは[どんどんよくなっています][1] ！Hueの次のリリース（または既に[Githubのマスター][2] にある）では、あなたは、Hueの[Mustache][3]のバージョンに追加機能を加えることができるようになり、HTMLの表示で直接関数を呼び出すことができます。どのように使用するのかを見てみましょう！以下のように、この例ではHTMLの結果ウィジェットでYelpのデモデータを使用したダッシュボードを追加します

[<img class="aligncenter size-large wp-image-2794" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.29.47-1024x684.png" alt="Screenshot 2015-07-27 15.29.47" width="1024" height="684" data-wp-pid="2794" />][4]

私たちは見た目を良くするため、それぞれのレビューにグラフィカルな星の評価とレストランの[静的なGoogle Map][5]を作りたいと思っています。CSS/JSタブで、私たちは新しいMustacheの機能である &#8216;hue\_fn\_renderStars&#8217; と &#8216;hue\_fn\_renderMap&#8217; を指定することができます&#8217;:

<pre><code class="xml">&lt;script&gt;
  viewModel.additionalMustache = function (item) {
    if (Mustache == "undefined") {
      return;
    }
 
    item.hue_fn_renderStars = function () {
      return function (val) {
        var stars = parseInt(Mustache.render(val, item));
        var html = '';
        for (var i=0;i&lt;stars;i++){
          html += '&lt;i class="fa fa-star"&gt;&lt;/i&gt;';
        }
        return html; 
      }
    };
   
    item.hue_fn_renderMap = function () {
      return function (val) {
        var coords = Mustache.render(val, item);
        return '&lt;img src="https://maps.googleapis.com/maps/api/staticmap?center=' + coords + '&zoom=14&size=300x300&markers=color:red%7C' + coords + '"&gt;';
      }
    };
  }
&lt;/script&gt;
</pre>

追加のMustache関数の名前に &#8216;fue\_fn\_&#8217; をプレフィックスにすることが非常に重要で、これでHueがピックアップして処理できるようになります。HTMLタブではこのように記述します:

<pre><code class="xml">&lt;div class="row-fluid"&gt;
        &lt;div class="row-fluid"&gt;
         &lt;div class="span10"&gt;
           &lt;h4&gt;{{name}} {{#renderStars}}{{stars}}{{/renderStars}}&lt;/h4&gt;
           &lt;span class="muted"&gt;{{text}}&lt;/span&gt;
         &lt;/div&gt;
        &lt;div class="span2"&gt;{{#renderMap}}{{latitude}},{{longitude}}{{/renderMap}}&lt;br/&gt;{{full_address}}&lt;/div&gt;
        &lt;/div&gt;
        &lt;br&gt;
       &lt;/div&gt;
</pre>

ご覧いただいているように、新しく追加された機能は{{#renderStars}} {{/ renderStars}} と {{#renderMap}} {{/ renderMap}}を用いて呼び出すことができます。そしてたったこれらのコード数行で結果の表示ははるかに良くなりました！

[<img class="aligncenter size-large wp-image-2792" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.51.21-1024x684.png" alt="Screenshot 2015-07-27 15.51.21" width="1024" height="684" data-wp-pid="2792" />][6]

HTMLテンプレート内の関数宣言の間にある文字列にアクセスするには **Mustache.render(val, item)**を参照する必要があります。
  
例えば、&#8217;if&#8217; のような条件関数を行ってその中で変数を評価したい場合、このようにすることができます

<pre><code class="xml">&lt;script&gt;
  viewModel.additionalMustache = function (item) {
    if (Mustache == "undefined") {
      return;
    }
 
    item.hue_fn_if = function () {
      return function (val) {
        var isTrue = $.trim(Mustache.render(val, item)) == 'true';
        return  isTrue ? "The condition is true!" : "No, it's false";
      }
    };
  }
&lt;/script&gt;
</pre>

そして、HTMLタブで使用します

<pre><code class="xml">{{#if}}{{field_to_test}}{{/if}}
</pre>

HTMLの結果ウィジェットで可能性は無限大です！:)いつものように、コメントとフィードバックは [hue-user][7] メーリングリストや[@gethue][8]までお気軽に！

 [1]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
 [2]: https://github.com/cloudera/hue
 [3]: https://github.com/janl/mustache.js/
 [4]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.29.47.png
 [5]: https://developers.google.com/maps/documentation/staticmaps/intro
 [6]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.51.21.png
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue