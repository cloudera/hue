---
title: 継続的インテグレーションにより JavaScript モジュールの互換性ライセンスと絶対パス以外のチェックを自動化
author: Romain
type: post
date: 2020-06-22T00:00:00+00:00
url: /automated-checking-javascript-licenses-absolute-paths-continuous-integration/
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
#  - Version 4.8

---

インターフェースビルダーの皆さん、こんにちは。

Hue プロジェクトのリソースと品質のスケールを支援するために、継続的インテグレーション (CI) と自動化への投資を継続して行っています。この1年では、[統合されたコミットフロー](https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/) と、[Circle CI](https://circleci.com/gh/cloudera/hue) によって自動的に実行される一連の[リンクチェック](https://gethue.com/checking-dead-links-automatically-continuous-integration/)を追加することで、多くの改善が行われました。

ここでは、JavaScript の成果物が正しいライセンスを持ち、絶対パスが含まれていないことを自動的にチェックする方法についての最新情報をご紹介します。

## ライセンス

Hue は [Apache 2 ライセンス](https://www.apache.org/licenses/LICENSE-2.0)のプロジェクトであり、他のプロジェクトに貢献したり、他のプロジェクトへの組み込みが容易にできます。一つの注意点として、GPLやLGPLのような、寛容ではないライブラリをバンドルしないように注意する必要があります。それらを見逃さないようにするために、新しい [check-license](https://github.com/cloudera/hue/tree/master/tools/license) は、すべての JavaScript モジュールが互換性があるかどうかを検証しています。

    npm run check-license

これは、簡単に [Hue CI](https://github.com/cloudera/hue/blob/master/.circleci/config.yml#L124) に簡単に統合されます:

    - run:
        name: run npm license checker
        command: |
          cd /usr/share/hue
          npm run check-license

![ci nmp license checker](https://cdn.gethue.com/uploads/2020/06/ci-nmp-license-checker.png)

## 絶対パス

ビルド機の完全なファイルパスを含んだリソース成果物を出荷しないことは良い習慣です。これにより、成果物は移植性があり、不要な情報を漏らさないことを保証するのに役立ちます。

Hue は既に [removeNPMAbsolutePaths](https://github.com/juanjoDiaz/removeNPMAbsolutePaths) スクリプトを活用していますが、しかし、これには Vue.js によって導入されたパスが抜けていました。最近この問題に対処するため、短い追加のチェック [check-absolute-paths](https://github.com/cloudera/hue/tree/master/tools/detect-absolute-paths) が追加されました。

    npm run check-absolute-paths

そして、CI にも追加されました。

    - run:
        name: run npm absolute path detection
        command: |
          cd /usr/share/hue
          npm run check-absolute-paths

このようにすることで、より多くの開発時間を後に取っておくことができます！

お好みの CI プロセスは何ですか？フィードバックはありますか？お気軽にこのブログや[@gethue](https://twitter.com/gethue)までコメントしてください!
