---
title: Webserver スタックのアップグレード時のプロセスと学び - Django のアップグレード (1.11 から 3.1)
author: Hue Team
type: post
date: 2021-03-09T00:00:00+00:00
url: /blog/2021-03-09-process-and-learnings-when-upgrading-the-webserver-stack-django-upgrade-1-to-3
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.10
  - Development

---

Hue プロジェクトは約[10年前](/blog/2020-01-28-ten-years-data-querying-ux-evolution/) に開始されました。その間にいくつかの技術が古くなったり、非推奨になったりしたため、HUE の明るい未来のためにそれらをアップグレードする必要がありました。その中でも [Django](https://www.djangoproject.com/) のアップグレードは最も重要な者の一つでした。アップグレード前は Django 1.11 を使用していましたが、2020年4月に延長サポートが終了しました。
![Djangoのロードマップ](https://cdn.gethue.com/uploads/2021/03/Django_roadmap.png)

## ゴール

* 1.11 のコンパイル/事項が可能ななま Django 3.1 (最新) で Hue が動作すること。

## アップグレードの理由

* 古いバージョンである [Django 1.11 は非推奨](https://www.djangoproject.com/download/#supported-versions)です。(例: セキュリティアップグレードや改善が受けられなくなります)。
* Django 1.11 には Python 2 が必要ですが、これも[非推奨](https://docs.djangoproject.com/en/3.1/faq/install/#what-python-version-should-i-use-with-django)です。
* [新しい機能、バグフィックス、改善](https://docs.djangoproject.com/en/dev/internals/deprecation/)が追加されています。
* 新しい Django のリリースが利用可能になるたびにアップグレードすると、コードベースを最新に保つことができ、将来のアップグレードの負担が軽減されます。
* 古いバージョンの Django をサポートしていない機能やライブラリもあります。(例: [DjangoRest framework](https://www.django-rest-framework.org/#requirements))。

## 課題

* 下位互換性を壊さないようにする。すなわち、同じコードベースで両方のバージョンをサポートする（選択肢がない場合は sys.version_info[0] < 3 スイッチを使用する)。
* 私たちの製品の依存関係の中には Django の新しいバージョンをまだサポートしていなものがあります。このような場合は、依存関係がある製品の新しいバージョンがリリースされるまで待たなければならないかもしれません。

## 計画

* 大きなトレードオフ:
  * Hue の Python 3 のビルドは Django 3 に移行する
  * Python 2 は Django 1.11 のまま (Django 1.11 は Python 2 をサポートする最新バージョンなので)
* ゆっくりではあるがしかし完璧に、後戻りしないように、私たちは Django を 1.11から 2.0、2.0から2.1、2.1から2.2、2.2から3.0、3.0から3.1へと段階的にアップグレードすることにしました。
* 次のバージョンにアップグレードする前に、現在の Django のバージョンで発生した deprecation の警告を解決し、google sheet に保存します。
* 警告を解決したら、計画通りに Django を次のバージョンへとアップグレードします。
* 両方のバージョン（最後のバージョンとアップグレードしたバージョン）について、全ての[ユニットテスト](https://docs.gethue.com/developer/development/#testing)を実行します。テストが失敗した場合は、ユニットテストかアップグレードした関連部分の何かを修正する必要があります。
* ビルド、パッケージ化、テストを行うための一貫した自動化の方法として [CircleCI](https://circleci.com/product/#how-it-works) を使用しています。
  * ![Passed CircleCi](https://cdn.gethue.com/uploads/2021/03/Passed_CircleCi.png)
  * 各コミットは CircleCI をパスしており、上のスクリーンショットでは CircleCI が両方のバージョン(build-py3.6 -> Django 3 and build -> Django 1.11)のコードをチェックしていることがわかります。
  * ![Failed CircleCi](https://cdn.gethue.com/uploads/2021/03/Failed_CircleCi.png)
  * そして、このスクリーンショットでは、Django 1.11 (build) でコミットが失敗していることがわかります。これは、私たちのコードが Django 1.11 で失敗していることを示しているので、それに応じてコードを変更する必要があります。
* 以上の手順を毎回行えば、新しいバージョンに対応することができます。
* Rinse and repeat （訳注: リンスは２度をお勧めします) :)

## 主な変更と学んだこと

* Django 1.11 から 2.0
  * この移行では、主に2種類のアップグレードの修正が必要です
    * 機能的な引数の追加や非推奨
    * 古い依存関係が新しいバージョンの Django をサポートしていない
  * しかし、“settings.MIDDLEWARE_CLASSES を使った古い形式のミドルウェアは非推奨” という大きな変更点があったので、2つの方法がありました。
    * 自分でミドルウェアを書く。
    * Django 1.10 形式のミドルウェアをアップグレードする。
  * 私たちは後方互換性を求めているので後者の方法をとり、[instructions](https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware)に注意深く従いました。


* Django 2.0 から 2.1
  * このアップグレードでは、“desktop.auth.backend.AllowFirstUserDjangoBackend.authenticate() が位置的な `request` 引数 を受け入れる必要がある“ という大きな変更があり、Python 2 + Django 1.11 と Python 3 + Django 2.1 の両方でコンパイルできるようにすることが課題となったので、sys.version_info[0] フラグ (つまり Python のバージョン) を使ってこの問題を解決しました。
    * しかし、上記のアップグレードの際、LDAP 認証機能を見落としていたため、Django 3 になってからこの問題が発生しました。この問題は解決できましたが、本当の教訓は、可能な限り全てのものにユニットテストを追加することで、LDAP 認証用のモックユニットテストを追加しました。


* Django 2.1 から 2.2
  * 大きな問題は Django の admin アプリに関するものでした。基本的に Django 2.2 では admin アプリでエラーが発生していたので、mako テンプレートが原因ではないかと考えましたが、Django admin をそのようには使用しておらず、mako を[Vue.js](https://gethue.com/blog/vue3-build-cli-options-composition-api-template-web-components-hue/) に置き換えることもしていなかったので、これを無効化して、将来必要にあったら追加することを考えて進めました。


* Django 2.2 から 3.0
  * この移行では、‘django-babel’ という名前のサードパーティの依存関係が Django 2.2 までしかサポートしていないというエラーが出ました。議論の結果、[フォーク](https://github.com/gethue/django-babel)して setup.py ファイルを適宜変更すれば Django 3.0 で動作するようになることがわかりました。


* Django 3.0 から 3.1
  * 大きな変更はなく、‘STATICFILES_STORAGE’ が CachedStaticFilesStorage からManifestStaticFilesStorage に変わっただけでした。

## それでは Hue with Django 3 を試してみましょう！
  ```
  git clone https://github.com/cloudera/hue.git   # Clone the Hue repository
  export PYTHON_VER=python3.8                     # Before build set the Pyhton_VER like
  make apps                                       # build the apps
  ./build/env/bin/hue runserver
  ```
  注: 問題が発生した場合はこちらの[リンク](https://docs.gethue.com/developer/development/)を参照して下さい。

</br>
</br>

ご意見や質問がありましたらお気軽にこちら、あるいは <a href="https://github.com/cloudera/hue/discussions">Discussions</a> までコメントして下さい。<a href="https://docs.gethue.com/quickstart/">quick start</a> で SQL をクエリして下さい!


どうぞよろしくお願いします！

Ayush from the Hue Team
