---
title: Hue API：いくつかの組み込みコマンドを実行する
author: Hue Team
type: post
date: 2015-02-26T00:13:42+00:00
url: /hue-api-execute-some-builtin-commands-2/
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
  - Hueには、サービスの管理を簡単にするためのコマンドセットが付属しています。これはコマンドセットを使用する方法についてのクイックガイドです。
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
  - Programming
  - SDK

---
Hueには、サービスの管理を簡単にするためのコマンドセットが付属しています。これはコマンドセットを使用する方法についてのクイックガイドです。

&nbsp;

## 始める

ICMを使用している場合は、正しいHueを指すためにこの変数をエクスポートします:

<pre><code class="bash">cd /opt/cloudera/parcels/CDH/lib/</pre>

<pre><code class="bash">HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id
echo $HUE_CONF_DIR
export HUE_CONF_DIR</pre>

ここで<id>はhue-HUE_SERVERのための、プロセスディレクトリ内の最新のIDです。

CMを使用していない場合、通常はHueのホームのルートを追加します:

<pre><code class="bash">/usr/lib/hue</pre>

注意：

あなたは、コマンドのログのためにローカルディレクトリへのアクセス権が必要になることがあります。例:

<pre><code class="bash">cd /tmp</pre>

&nbsp;

引数なしでhueコマンドを実行すると、すべてが一覧表示されます:

<pre><code class="bash">./build/env/bin/hue

...

[auth]
 changepassword
 createsuperuser

[beeswax]
 beeswax_install_examples
 close_queries
 close_sessions

[desktop]
 config_dump
 config_help
 config_upgrade
 create_desktop_app
 create_proxy_app
 create_test_fs
 kt_renewer
 runcherrypyserver
 runcpserver
 runpylint
 sync_documents
 test
 version

[django]
 cleanup
 compilemessages
 createcachetable
 dbshell
 diffsettings
 dumpdata
 flush
 inspectdb
 loaddata
 makemessages
 reset
 runfcgi
 runserver
 shell
 sql
 sqlall
 sqlclear
 sqlcustom
 sqlflush
 sqlindexes
 sqlinitialdata
 sqlreset
 sqlsequencereset
 startapp
 startproject
 validate

[django_extensions]
 clean_pyc
 compile_pyc
 create_app
 create_command
 create_jobs
 describe_form
 dumpscript
 export_emails
 generate_secret_key
 graph_models
 mail_debug
 passwd
 print_user_for_session
 reset_db
 runjob
 runjobs
 runprofileserver
 runscript
 runserver_plus
 set_fake_emails
 set_fake_passwords
 shell_plus
 show_templatetags
 show_urls
 sqldiff
 sync_media_s3
 syncdata
 unreferenced_files

[django_openid_auth]
 openid_cleanup

[hbase]
 hbase_setup

[indexer]
 indexer_setup

[oozie]
 oozie_setup

[pig]
 pig_setup

[search]
 search_setup

[south]
 convert_to_south
 datamigration
 graphmigrations
 migrate
 migrationcheck
 schemamigration
 startmigration
 syncdb
 testserver

[spark]
 livy_server

[useradmin]
 import_ldap_group
 import_ldap_user
 sync_ldap_users_and_groups
 useradmin_sync_with_unix
</pre>

## サーバを起動する

テストサーバを記載した場合、ポート8000がデフォルトです:

<pre><code class="bash">./build/env/bin/hue runserver</pre>

運用サーバーを記載した場合、ポート8888がデフォルトです:

<pre><code class="bash">./build/env/bin/hue runcpserver</pre>

これらのコマンドは、[ How to get started page][1]に詳しく記載されています。

## サンプルをインストールする

&#8216;_setup &#8216;で終わるすべてのコマンドは、特定のアプリケーションのサンプルをインストールします。

<pre><code class="bash">./build/env/bin/hue search_setup</pre>

Hiveの場合、sample\_07とsample\_08テーブルとSQLのクエリをインストールするためには次のように入力します:

<pre><code class="bash">./build/env/bin/hue beeswax_install_examples</pre>

**注**:

これらのコマンドは [Web UI][2]から直接アクセスすることもできます。

[<img class="aligncenter size-full wp-image-1108" src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080615.png" alt="Screenshot from 2014-04-09 08:06:15" width="757" height="634" data-wp-pid="1108" />][3]

## パスワードを変更する

このコマンドは、[How to change or reset a forgotten password][4]のブログポストで詳細に説明されています:

<pre><code class="bash">./build/env/bin/hue changepassword</pre>

## Hiveクエリをクローズする

このコマンドは[HiveとImpalaクエリのライフサイクル][5]のブログポストで詳しく説明されています:

<pre><code class="bash">./build/env/bin/hue close_queries</pre>

<pre><code class="bash">./build/env/bin/hue close_sessions</pre>

## テストを実行する

このコマンドは[How to run the tests][6]のブログポストで詳細に説明されています:

<pre><code class="bash">./build/env/bin/hue test</pre>

## データベースに接続する

このコマンドは [How to manage the database with the shell][7]のブログポストで詳細に説明されています:

<pre><code class="bash">./build/env/bin/hue test</pre>

&nbsp;

&nbsp;

ご質問はありますか？[hue-user][8]または[@gethue][9]までお気軽にお問い合わせください！

 [1]: https://github.com/cloudera/hue#getting-started
 [2]: https://gethue.com/tutorial-live-demo-of-search-on-hadoop/
 [3]: https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080615.png
 [4]: https://gethue.com/password-management-in-hue/
 [5]: https://gethue.com/hadoop-tutorial-hive-and-impala-queries-life-cycle-2/?lang=ja "HiveとImpalaクエリのライフサイクル"
 [6]: https://gethue.com/tutorial-how-to-run-the-hue-integration-tests/
 [7]: https://gethue.com/how-to-manage-the-hue-database-with-the-shell/
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://twitter.com/gethue
