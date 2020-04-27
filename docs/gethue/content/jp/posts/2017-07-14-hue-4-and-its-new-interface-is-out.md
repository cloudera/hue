---
title: Hue 4 とその新しいインターフェイスが公開されました！
author: Hue Team
type: post
date: 2017-07-14T04:42:59+00:00
url: /hue-4-and-its-new-interface-is-out/
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
  - この最新のHueのアップデートでは、SQL開発者とアナリスト向けのインテリジェントなエディターとセキュリティに重点を置いていました。バージョン3.12 に3000以上のコミットが入りました！
categories:
  - Hue 4.0

---
ビッグデータ探検家の皆さん、

&nbsp;

Hueチームはすべての貢献者に感謝し、Hue 4がリリースできて嬉しく思います![<img class="aligncenter size-full wp-image-2988" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo (copy)" width="85" height="63" data-wp-pid="2988" />][1]

この最新のHueのアップデートでは、SQL開発者とアナリスト向けのインテリジェントなエディターとセキュリティに重点を置いていました。バージョン[3.12][2] に[3000][3]以上のコミットが入りました！tarball版のリリースを入手して実行してください！

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://www.dropbox.com/s/r4d6ox5kyfng454/hue-4.0.0.tgz?dl=0" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

<span style="font-weight: 400;">これらはより詳細なブログ記事へのリンクを含んだ主な改善点の一覧です。すべての変更については<a href="http://cloudera.github.io/hue/docs-4.0.0/release-notes/release-notes-4.0.0.html">リリースノート</a> を参照してください。また、<a href="http://demo.gethue.com/">demo.gethue.com</a>をオープンしてください。</span>

&nbsp;

# インターフェイス

新しいレイアウトはインターフェイスを簡素化し、単一の完結なページになりました。

様々なアプリケーションは4つのアプリケーションに分類されています。:

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li>
      エディタ
    </li>
    <li>
      ブラウザ
    </li>
    <li>
      ダッシュボード
    </li>
    <li>
      スケジューラー
    </li>
  </ul>
  
  <p>
    &nbsp;
  </p>
  
  <ul class="itemizedlist">
    <li class="listitem">
      一番上の検索バーと左側のアシストは、素早い検索とすべてのデータの参照を支援します。
    </li>
    <li class="listitem">
      各ユーザーは、お気に入りのアプリケーションをデフォルトのアクション/ランディングページとして設定できます。
    </li>
    <li class="listitem">
      古いHue 3のUIは引き続き使用でき、Hue 4には100%後方互換性があります。
    </li>
    <li class="listitem">
      新しいHue 4のUIへの切り替えはグローバルレベルで決定するか、または各ユーザーは、UIのひとつをデフォルトとして独立して前後のバージョンに切り替えることができます。
    </li>
    <li class="listitem">
      /hue の接頭辞がついているすべてのURLはHue 4を指し、ついていないものは Hue 3を指しています。
    </li>
    <li class="listitem">
      /hue/editor (Hue 4) → /editor (Hue 3)　のように、ページの接頭辞を削除するだけで Hue 3バージョンのページにたどり着くことができます。
    </li>
  </ul>
  
  <p>
    詳細は今後のブログをご覧ください。
  </p>
  
  <p>
    <a href="https://cdn.gethue.com/uploads/2016/04/hue4_editor.png"><img class="aligncenter size-full wp-image-4777" src="https://cdn.gethue.com/uploads/2016/04/hue4_editor.png" alt="" width="1525" height="986" data-wp-pid="4777" /></a>
  </p>
</div>

# エディタ

## SQL

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      エディタに複数のステートメントが存在している場合、カーソルの位置によって実行されるアクティブなステートメントが決定されます。複数のステートメント（例：一連のCREATE テーブル）を順番に実行するには手作業で全てを選択するか、ショートカット（Ctrl / Cmd+Aなど）を使用してすべてを選択する必要があります。
    </li>
    <li>
      <span class="goog-text-highlight">それについての詳細は、今後のブログ記事をご覧ください。</span>
    </li>
  </ul>
</div>

## Pig

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      宣言とマクロの高度な使用は、新しいエディタのオートコンプリートではサポートされていません。過去のスクリプトは新しいエディタに変換されているか、Hue 3のUIにあります。
    </li>
  </ul>
</div>

## Job Designer

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      MapReduce、Java、Spark、Sqoop1などのアクションが新しいエディタに表示されるようになりました。過去のスクリプトは新しいエディタに変換されているか、Hue 3のUIにあります。
    </li>
  </ul>
  
  <h2>
    Oozie とスケジューリング
  </h2>
  
  <div class="itemizedlist">
    <ul class="itemizedlist">
      <li class="listitem">
        エディタから保存されたクエリ（Hiveクエリなど）は、手動でHDFS上のファイルをコピーすることなく、アクションにドラッグアンドドロップできます。
      </li>
    </ul>
  </div>
</div>

# ブラウザ

## ジョブ

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      新しいブラウザは、以前のJob BrowserとOozie ダッシュボードを結合しました。アプリは単一のページになり、直感的に使えるようになりました。ミニジョブブラウザは、ページから離れることなくジョブを見ることができるようになりました。
    </li>
  </ul>
</div>

## S3

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      V2リージョンに資格情報が設定されている場合はV2リージョンをサポートします。V4エンドポイント用に構成されている場合は、そのリージョンのエンドポイントのバケットのみにアクセスできます。
    </li>
  </ul>
</div>

# その他

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      ファイルからパーティションテーブルを作成する
    </li>
    <li class="listitem">
      importerでテーブルを作成すると、Impalaのメタデータが自動的に更新されるようになった
    </li>
    <li class="listitem">
      SQLオートコンプリートでより高度なコーナーケースを扱う
    </li>
    <li class="listitem">
      Hueとは別のホスト上のロードバランサがSSLで動作するようになった
    </li>
    <li class="listitem">
      SQLクエリ履歴にページ付けが追加された
    </li>
    <li class="listitem">
      create tableのようなバッチ処理がバックグラウンドタスクとして実行されるようになった
    </li>
    <li class="listitem">
      500件のバグ修正
    </li>
  </ul>
</div>

&nbsp;

&nbsp;

さらにその先へ!

&nbsp;

プロジェクトに貢献してくださった皆さん、フィードバックを送ってくれたり[hue-user][4] メーリングリストや [@gethue][5]に参加してくれた方々に、いつものように感謝しています！

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://gethue.com/hue-3-12-the-improved-editor-for-sql-developers-and-analysts-is-out/
 [3]: http://cloudera.github.io/hue/docs-4.0.0/release-notes/release-notes-4.0.0.html#_list_of_3215_commits
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue