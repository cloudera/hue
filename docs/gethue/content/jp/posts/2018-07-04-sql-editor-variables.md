---
title: SQLエディタでの変数
author: Hue Team
type: post
date: 2018-07-04T02:16:35+00:00
url: /sql-editor-variables/
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
sf_custom_excerpt:
  - |
    SQL愛好家のみなさん、こんにちは！
    
    私たちは、エディタの使い勝手を改善する方法を少しずつ模索してきました。
    
    共有
    Hue 4.1では、保存したクエリを他のHueユーザーと一緒に共有する機能を追加し、協力して仕事を分かち合うことができるようになりました。共有するには、エディタの右側のメニューにアクセスします。
categories:
  - Editor / Notebook
  - Hive
  - Hue 4.1
  - Hue 4.2
  - Hue 4.3
  - Impala

---
原文: <a href="https://gethue.com/sql-editor-variables/" target="_blank" rel="noopener">SQL editor variables</a>

_2018年6月5日更新：Hue 4.3 にブール変数が導入されました_

<p class="p1">
  SQL愛好家のみなさん、こんにちは！
</p>

<p class="p1">
  私たちは、エディタの使い勝手を改善する方法を少しずつ模索してきました。
</p>

## 共有 {.p1}

Hue 4.1では、保存したクエリを他のHueユーザーと一緒に共有する機能を追加し、協力して仕事を分かち合うことができるようになりました。共有するには、エディタの右側のメニューにアクセスします。

[<img class="alignnone size-full wp-image-5323" src="https://cdn.gethue.com/uploads/2018/04/btn_share.png" alt="" width="263" height="231" />][1]

<p class="p1">
  一旦そこにいけば、あなたはHueのユーザのオートコンプリートを行い、書き込みアクセス権を持たせるべきかどうかを決めることができます。
</p>

[<img class="alignnone size-medium wp-image-5318" src="https://cdn.gethue.com/uploads/2018/04/modal_share.png" alt="" width="1760" height="445" />][2]

## 変数 {.p1}

<p class="p1">
  しばらく前からSQLのクエリで変数が定義できるようになっていたので、クエリ内でパラメーターを簡単に設定できました。また、変数は、他のユーザーが必要な値で共有のクエリをカスタマイズできるようにするための優れた方法です。
</p>

[<img class="alignnone size-medium wp-image-5319" src="https://cdn.gethue.com/uploads/2018/04/variables_basic.png" alt="" width="504" height="191" />][3]

<pre><code class="bash">select * from web_logs where country_code = "${country_code}"
</pre>

<p class="p1">
  Hue 4.1では、変数にデフォルト値を追加する機能が追加されました。デフォルト値には2種類あります。
</p>

**単一の値**

<pre><code class="bash">select * from web_logs where country_code = "${country_code=US}"
</pre>

**複数の値**

<pre><code class="bash">select * from web_logs where country_code = "${country_code=CA, FR, US}"
</pre>

<p class="p1">
  さらに、複数の変数の値で表示されるテキストを変更することができます。
</p>

<pre><code class="bash">select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"
</pre>

[<img class="alignnone size-full wp-image-5321" src="https://cdn.gethue.com/uploads/2018/04/variables_multi.png" alt="" width="858" height="259" />][4]

<p class="p1">
  Hue 4.3では、変数名をクリックしたときに列の支援を表示する機能が追加されました。これは使用する値を判断する際に便利です。
</p>

[<img class="alignnone size-full wp-image-5322" src="https://cdn.gethue.com/uploads/2018/04/variables_popover.png" alt="" width="518" height="583" />][5]

<p class="p1">
  あなたが私たちのようであれば、日付とタイムスタンプの正しい書式を覚えておくことはあなたが気にする最後のことです。前述の種類のためにメタストア内で列のデータ型が利用可能な場合、Hueはデフォルト値を今日の日付に設定し、カレンダーから日付を選択することができます。
</p>

[<img class="alignnone size-medium wp-image-5320" src="https://cdn.gethue.com/uploads/2018/04/variables_calendar.png" alt="" width="441" height="406" />][6]

<p class="p1">
  Hue 4.3では、ブール値をデータ型として使用する際にチェックボックスを表示するように少しの改善を行いました。
</p>

[<img class="size-full wp-image-5387" src="https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-04-at-4.52.44-PM.png" alt="" width="547" height="207" />][7]

## ヘルプ {.p1}

最後に、これらの新しい機能の使い方を忘れてしまっても気にしないでください。エディタに新しいヘルプボタン [<img class="alignnone size-full wp-image-5316" src="https://cdn.gethue.com/uploads/2018/04/button_help.png" alt="" width="203" height="31" />][8]を追加しました。この情報などを要約して表示します。
  
[<img class="aligncenter size-full wp-image-5390" src="https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-05-at-8.59.40-AM.png" alt="" width="1235" height="676" />][9]

<p class="p1">
  いつものように、ご不明な点があれば、こちら、あるいは <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a> メーリングリストや <a href="https://twitter.com/gethue">@gethue</a> までお気軽にコメントをお寄せください！
</p>

 [1]: https://cdn.gethue.com/uploads/2018/04/btn_share.png
 [2]: https://cdn.gethue.com/uploads/2018/04/modal_share.png
 [3]: https://cdn.gethue.com/uploads/2018/04/variables_basic.png
 [4]: https://cdn.gethue.com/uploads/2018/04/variables_multi.png
 [5]: https://cdn.gethue.com/uploads/2018/04/variables_popover.png
 [6]: https://cdn.gethue.com/uploads/2018/04/variables_calendar.png
 [7]: https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-04-at-4.52.44-PM.png
 [8]: https://cdn.gethue.com/uploads/2018/04/button_help.png
 [9]: https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-05-at-8.59.40-AM.png