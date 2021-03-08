---
title: 継続的な統合による自動的なドキュメントとウェブサイトのデッドリンクのチェック
author: Romain
type: post
date: 2020-03-11T00:00:00+00:00
url: /checking-dead-links-automatically-continuous-integration/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.7

---

データクランチャーの皆さんこんにちは。

継続的インテグレーション (CI) と自動化は、ソフトウェアプロジェクトのリソースと品質を大幅にスケール可能にする投資です。この1年で、[統合されたコミットフロー](https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/)、およびJavaScriptのLintのチェックのような一連のチェックの追加、Python 3 テストの自動実行など、多くの改善が見られました。

また、すべてのつなぎ込み (Plumbling) がすでに行われているため、開発者が自分自身で多くのテストの追加を奨励する好循環を生み出しています。(例えば、今年の初めから200以上が追加されています)。

![CI workflow](https://cdn.gethue.com/uploads/2020/03/ci-both-python.png)
CI ワークフロー

![List of CI checks](https://cdn.gethue.com/uploads/2020/03/ci-checks-lints-docs.png)
CI チェックの一覧

自動化リストでの次の項目は、以前は[手動](https://gethue.com/easily-checking-for-deadlinks-on-docs-gethue-com/)で行なっていた https://docs.gethue.com と https://gethue.com/ のデッドリンクの自動チェックでした。.


![New website deadlinks check](https://cdn.gethue.com/uploads/2020/03/ci-linting-docs.png)
ウェブサイトの新しいリンク切れチェック


[アクションスクリプト](https://github.com/cloudera/hue/blob/master/tools/ci/check_for_website_dead_links.sh) の全体は以下のようになっています:

* ウェブサイトのドキュメントの変更を含む新しいコミットがあるかどうかを確認する
* 次に、ローカルにサイトを提供するために`hugo` を起動する
* `muffet`を実行してリンクをクロールしチェックする

![Link checking failure](https://cdn.gethue.com/uploads/2020/03/ci-link-failure.png)
リンクチェックの失敗

注: いくつかの外部サイト(例:https://issues.cloudera.org/browse/HUE には多くの参照が含まれています) を妨害しないように、URLのブラックリストとクローラーの同時接続数を減らすと便利です。



お好みのCIプロセスは何ですか? フィードバックがあれば、このブログまたは[@gethue](https://twitter.com/gethue)まで気軽にコメントして下さい!
