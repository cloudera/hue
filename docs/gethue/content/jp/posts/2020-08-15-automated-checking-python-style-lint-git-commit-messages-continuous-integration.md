---
title: Git コミットでの Python のスタイルとタイトル形式を自動的にチェックする
author: Romain
type: post
date: 2020-08-15T00:00:00+00:00
url: /automated-checking-python-style-and-title-format-of-git-commits-continuous-integration/
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

クエリエンジニアの皆さん、こんにちは。

継続的インテグレーション (CI) と自動化への投資は、Hue プロジェクトのリソースと品質を拡大を支援するために続けられています。この1年では次のような大きな改善が見られました。

* [Circle CI](https://circleci.com/gh/cloudera/hue) によって自動的に実行される[コミットフロー](https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/)
* gethue.com と demo.gethue.com ウェブサイトの[リンクのチェック](https://gethue.com/checking-dead-links-automatically-continuous-integration/)
* JavaScript のスタイルとアーティファクトの[ライセンスチェック](/automated-checking-javascript-licenses-absolute-paths-continuous-integration/)

ここでは、**Python API のコーディング規約**が全員に守られているかどうかを確認する方法や、**git commitのタイトルの形式**についての最新情報をお知らせします。

## Python のリント

Hue は、コーディング標準をチェックするためのオープンソースプログラムである [Pylint](https://www.pylint.org/) を活用しています。これには `.pylintrc` ファイルで選択してカスタマイズ可能な一連のルールが付属しています。

コミットの変更が規約に従っているかどうかを早期に発見するために、ほとんどのコードエディタでは、いくつかのプラグインで Pylint の設定を理解することができます。これは、ほとんどの時間を修正に費やしているあなたのためにも、エディタで早期にエラーを直接見ることができて便利です。

![Pylint indentation visual check](https://cdn.gethue.com/uploads/2020/08/pylint-indent.png)

## 一歩ずつ進める

Hue は10年以上の成熟したプロジェクトであり、コードベースのサイズのほとんどが、50%のPythonで構成されています。そのため、すぐに全てのコードのスタイルの問題を修正するのは負担が大きすぎるかもしれません。そのため、インクリメント戦略が採用されました。

* 新しいローカルでのコミットで更新されたファイルのみをリントする (差分だけでなく、ファイルの内容全体をリントする)
* 最小限のスタイル規約のみで開始する (基本的なルールのみ。基本が完了したら後から追加するルールを増やす)
  * C0326 (bad-whitespace)
  * W0311 (bad-indentation)
  * C0301 (line-too-long)


[check_for_python_lint.sh](https://github.com/cloudera/hue/blob/master/tools/ci/check_for_python_lint.sh) を実行する次のコマンドは、

    tools/ci/check_for_python_lint.sh

チェックに失敗した行をローカルに出力します。

    [10/Aug/2020 16`:22:17 -0700] runpylint    INFO     Running pylint with args: /home/romain/projects/hue/build/env/bin/pylint --rcfile=/home/romain/projects/hue/desktop/.pylintrc --disable=all --enable=C0301,C0326,W0311 --load-plugins=pylint_django -f parseable apps/beeswax/src/beeswax/api.py desktop/core/src/desktop/management/commands/runpylint.py
    ************* Module beeswax.api
    apps/beeswax/src/beeswax/api.py:144: [C0326(bad-whitespace), ] Exactly one space required after :
          {1:1}
            ^
    apps/beeswax/src/beeswax/api.py:236: [C0326(bad-whitespace), ] Exactly one space required before assignment
        response['status']= 0
                          ^
    apps/beeswax/src/beeswax/api.py:239: [C0326(bad-whitespace), ] Exactly one space required before assignment
        response['status']= 0
                          ^
    apps/beeswax/src/beeswax/api.py:436: [C0326(bad-whitespace), ] Exactly one space required before assignment
        response['message']= str(e)
                          ^
    apps/beeswax/src/beeswax/api.py:678: [C0301(line-too-long), ] Line too long (156/150)
    ************* Module desktop.management.commands.runpylint
    desktop/core/src/desktop/management/commands/runpylint.py:66: [C0301(line-too-long), ] Line too long (255/150)
    desktop/core/src/desktop/management/commands/runpylint.py:70: [C0326(bad-whitespace), ] Exactly one space required around assignment
        a={1:   3}
        ^
    desktop/core/src/desktop/management/commands/runpylint.py:70: [C0326(bad-whitespace), ] Exactly one space required after :
        a={1:   3}
            ^
    desktop/core/src/desktop/management/commands/runpylint.py:72: [W0311(bad-indentation), ] Bad indentation. Found 8 spaces, expected 6

    ------------------------------------------------------------------
    Your code has been rated at 9.86/10 (previous run: 9.88/10, -0.02)


スタイルの設定は [.pylintrc](https://github.com/cloudera/hue/blob/master/.pylintrc) に保存されます。

その後、全ての新しい変更に対して自動的に利用できるようにするには、CircleCi の [config.yml](https://github.com/cloudera/hue/blob/master/.circleci/config.yml#L109) の `run python lints` セクションにフックして、Hue の CI に簡単に統合します。

    - run:
        name: run python lints
        command: |
          cd ~/repo

          ./tools/ci/check_for_python_lint.sh /usr/share/hue


![ci pyling success no change](https://cdn.gethue.com/uploads/2020/08/ci-pylint-success.png)

## Git Commit のフォーマットチェック

コーディング規約と同様に、コミットのタイトルについても全員が同じ言語を使うことで、長期的には時間を節約することができます。

物事をシンプルに保つために2つの形式だけを選択しました。
* Jira 番号を含む従来のHueの形式
* 最後に標準のIDを含む GitHub のプルリクエスト

両方とも、変更の主な領域を記述するため、カッコ内にカテゴリを持つ必要があります。一例としてこのような形式です [docs], [hive], [docker], [ui]...

有効なメッセージの例は次の通りです:

    HUE-9374 [impala] Use 26000 as default for thrift-over-http
    [livy] Add numExecutors options (#1238)

いくつかの無効なものもあります (無効な組み合わせが多くなりやすいです):

    [impala] Use 26000 as default for thrift-over-http
    Use 26000 as default for thrift-over-http (#1238)
    HUE-9374 Use 26000 as default for thrift-over-http
    Add numExecutors options


チェックロジックは `commit-msg` [Git hooks](https://github.com/cloudera/hue/blob/master/tools/githooks) の一部です。

ローカルで自動的に git commit メッセージをチェックするには、フックをコピーするだけです。

    cp tools/githooks/* .git/hooks
    chmod +x .git/hooks/*

そして、まだマスターブランチにフックされていない新しいコミットに対してのみチェックを行うスクリプトを以下に示します。

    ./tools/ci/check_for_commit_message.sh

そして 100% 自動化するために CI に追加します。

    - run:
      name: run commit title format check
      command: |
          cd ~/repo

          ./tools/ci/check_for_commit_message.sh

![ci git title format fail](https://cdn.gethue.com/uploads/2020/08/ci-commit-format-check-fail.png)


これで、今後の開発時間がより短縮されました！

あなたのお気に入りの CI プロセスは何ですか？フィードバックがあれば、このページまたは [@gethue](https://twitter.com/gethue) で気軽にコメント下さい！

Romain from the Hue Team
