---
title: Hue 4.3で追加されたSQLの改善点
author: Hue Team
type: post
date: 2018-10-31T03:21:51+00:00
url: /additional-sql-improvements-in-hue-4-3/
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
sf_custom_excerpt:
  - Hue 4.3 ではSQLのエクスペリエンスを大幅に改善しました。前の記事ではいくつかの改良点を示しましたが、今回はエディタにおけるいくつかの新しい機能を紹介したいと思います。
categories:
  - Browser
  - Editor / Notebook
  - HDFS
  - Hive
  - Hue 4.3
  - Impala

---
<div class="post-info clearfix">
  <div class="comments-likes">
    <div class="comments-wrapper">
      <a href="https://gethue.com/additional-sql-improvements-in-hue-4-3/#comments">0 Comments</a>
    </div>
  </div>
</div><section class="article-body-wrap"> 

<div class="body-text clearfix">
  <p>
    SQL愛好家の皆さん、こんにちは！
  </p>
</div></section> 

[Hue 4.3][1] ではSQLのエクスペリエンスを大幅に改善しました。前の[記事][2]ではいくつかの改良点を示しましたが、今回はエディタにおけるいくつかの新しい機能を紹介したいと思います。

UDFリファレンスパネルを紹介した後、SQL構文のドキュメントも含めるような要望を受け取りました。特定のステートメントを書いている間に[言語リファレンス][3]を参照するのはよくあることですが、複数の画面を開いておくのは面倒です。可能な限り最高の体験を提供するために、完全なImpala SQL言語リファレンスをHueに含めることにしました。

## 組み込み Impala 言語リファレンス

右側のアシストパネルに言語リファレンスがあります。右側のパネル自体には新しくアイコンが左側に表示され、アクティブなアイコンをクリックすることで最小化できます。

この初期バージョンでは、一番上のフィルターへの入力はトピックのタイトルのみをフィルターします。以下は、selectステートメントでの結合（ジョイン）に関するドキュメントを検索する方法の一例です。

<div class="wp-caption aligncenter">
  <p>
    <img class="aligncenter size-full wp-image-5579" width="766" height="421" data-gifffer="https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_joins.gif" data-wp-pid="5579" />
  </p>
  
  <p class="wp-caption-text">
    新しい言語リファレンスパネル
  </p>
</div>

ステートメントを編集する際は、現在のステートメントの種類の言語リファレンスをすばやく見つける方法があります。最初の単語を右クリックだけで、以下のようなポップオーバーに参照が表示されます。

[<img class="aligncenter size-full wp-image-5580" src="https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png" alt="" width="776" height="495" />][4]

## 改善された列のサンプル

どんな種類の値が期待できるのかを調べるためのクエリを書くときに、列のサンプルを見ることができるのは非常に便利です。Hueは、サンプルデータに対していくつかの演算を実行できるようになりました。これにより min値とmax値だけでなく、distinctな値も表示できます。今後のリリースではさらに多くの操作が見込まれます。

<div class="wp-caption aligncenter">
  <p>
    <img class="aligncenter size-full wp-image-5581" width="766" height="523" data-gifffer="https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif" data-wp-pid="5581" />
  </p>
  
  <p class="wp-caption-text">
    distinctの（重複を排除した）サンプル値を表示する
  </p>
</div>

## エディターのダークモード

エディターにダークモードを導入しました！このモードは、最初は実際のエディタ領域に限定されています。これをHue全体で扱うように拡張することを検討しています。

<div id="attachment_5582" style="width: 810px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png"><img class="size-full wp-image-5582" src="https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png" alt="" width="800" height="388" /></a>
  
  <p class="wp-caption-text">
    新しいダークモード
  </p>
</div>

ダークモードに切り替えるには、エディターにフォーカスが当たっている時に `Ctrl-Alt-T`、または Mac では `Command-Option-T` を入力します。または、`Ctrl-`キー、または Mac では `Command-`キーを押しながら表示される設定メニューで制御することもできます。

これらの新しい機能が素晴らしいクエリを作成するのに役立つことを願っています。いつものように、ご質問やフィードバックがあれば、こちら、あるいは [hue-user][5] メーリングリストや[@gethue][6]までお気軽にコメントをお寄せください！

 [1]: https://gethue.com/hue-4-3-and-its-app-building-improvements-are-out/
 [2]: https://gethue.com/improved-sql-exploration-in-hue-4-3/
 [3]: https://impala.apache.org/impala-docs.html
 [4]: https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png
 [5]: http://groups.google.com/a/cloudera.org/group/hue-user
 [6]: https://twitter.com/gethue