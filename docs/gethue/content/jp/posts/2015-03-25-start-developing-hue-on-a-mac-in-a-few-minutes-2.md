---
title: 数分でHueの開発をMacで始める！
author: Hue Team
type: post
date: 2015-03-25T00:57:38+00:00
url: /start-developing-hue-on-a-mac-in-a-few-minutes-2/
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
  - あなたはすでに前提条件の全てをインストールしているかもしれませんが、私たちは初期状態のYosemite (10.10) のインストールから開始して、ほとんど時間をかけることなく、最後にはあなたのMacでHueを動作する方法を紹介しましょう！
categories:
  - Hue 3.8
  - Programming
  - SDK

---
あなたはすでに<a href="https://github.com/cloudera/hue#development-prerequisites" target="_blank">前提条件</a>の全てをインストールしているかもしれませんが、私たちは初期状態のYosemite (10.10) のインストールから開始して、ほとんど時間をかけることなく、最後にはあなたのMacでHueを動作する方法を紹介しましょう！

[<img class="aligncenter size-large wp-image-2359" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.11.26-1024x768.png" alt="Screenshot 2015-03-24 09.11.26" width="1024" height="768" data-wp-pid="2359" />][1]

私たちはHueが接続するために、既に全てのHadoopエコシステムのコンポーネントが含まれているCloudera公式の<a href="http://www.cloudera.com/content/cloudera/en/downloads/quickstart_vms.html" target="_blank">クイックスタートVM(Quickstart VM)</a>を使用します。もし、まだクイックスタートVM最新版を持っておらず、ダウンロードして実行していない場合は<a href="http://www.cloudera.com/content/cloudera/en/downloads/quickstart_vms.html" target="_blank">このリンク</a>にアクセスして、あなたに合うバージョンを選択して下さい。

その間に、Macをセットアップしましょう​​！

**ステップ1：Hueのリポジトリをクローンする**
  
HueのGithubのリポジトリをクローンするためには、システムにgitをインストールしている必要があります。Git（と他の多くのツール）はXcodeのコマンドラインツールに含まれています。インストールするにはターミナルを開いて以下を入力します:

<pre><code class="bash">xcode-select --install</pre>

ダイアログで「Install」を選択します。ターミナルに「“xcode-select: error: command line tools are already installed, use “Software Update” to install updates” 」というメッセージが出ている場合は、ほとんど既にうまくいっていることを意味しています。

ターミナルからあなたの全てのプロジェクトを保持しているディレクトリに移動し、下記を実行します:

<!--email_off-->

<pre><code class="bash">git clone https://github.com/cloudera/hue.git</pre>

<!--/email_off-->

これで、あなたのMacにはHueのソースコードがあります。

**ステップ2：Javaをインストールする**
  
ビルドプロセスの実行にはJavaを使用しています。Oracleから正しいダウンロードURLを取得する簡単な方法は、ターミナルから以下を実行することです:

<pre><code class="bash">java -version</pre>

その後表示されるダイアログで「More info」ボタンをクリックします。Oracleのウェブサイトでは、ライセンスに同意し、Mac OS XのJDKのリンクを選択します。DMGをダウンロードした後そのファイルをオープンして、インストールパッケージをダブルクリックします。ターミナルに戻り、もう一度入力します:

<pre><code class="bash">java -version</pre>

新たにインストールされたJDKのバージョンがあるでしょう。この執筆時点では、1.8.0_40です。

**ステップ3：前提条件をインストールする**
  
HueはXcodeのコマンドラインツールに含まれていないいくつかのライブラリをインストールする必要があるので、それらもインストールしなければなりません。これを行うにはMac OS X用のファンタスティックなオープンソースのパッケージマネージャである<a href="http://brew.sh" target="_blank">Homebrew</a>を使用ます。ターミナルからインストールします:

<pre><code class="bash">ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"</pre>

続行するにはパスワードを入力する必要があります。すインストールスクリプトによって提案されるので、実行します

<pre><code class="bash">brew doctor</pre>

すでにHomebrewをインストールしている場合は、以下を実行して更新します:

<pre><code class="bash">brew update</pre>

まず最初に、Maven 3をインストールする必要があります:

<pre><code class="bash">brew install maven</pre>

そして、MySQLの開発ライブラリも必要です:

<pre><code class="bash">brew install mysql</pre>

**ステップ4：Hueをコンパイルし、設定する**
  
ここで、ステップ1でgit cloneで作成されたHueのフォルダから以下を実行することにより、私たちはすべての要件に設定されているのでHueをコンパイルすることができます:

<pre><code class="bash">make apps</pre>

計画通りにすべてがうまくいくと、しばらくして「N static files copied to …」のような最後のビルドメッセージを見ることができるはずです。

[<img class="aligncenter size-large wp-image-2358" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.09.20-1024x768.png" alt="Screenshot 2015-03-24 09.09.20" width="1024" height="768" data-wp-pid="2358" />][2]

Hueには全てのサービスがローカルマシンを示しているデフォルトの[設定ファイル][3]が付属しています。今回私たちはサービスを動かすために仮想マシンを使用するので、いくつかの設定行を変更する必要があります。利便性のため、[こちら][4]に利用可能なファイルを用意しています。

単純に、あなたの hue/desktop/conf フォルダにこのファイルを上書きコピーします！

**ステップ5：/etc/hosts ファイルを設定する**
  
最後に行うことはクイックスタートVMを起動し、IPアドレスを取得することです:

[<img class="aligncenter size-large wp-image-2356" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-08.56.33-1024x688.png" alt="Screenshot 2015-03-24 08.56.33" width="1024" height="688" data-wp-pid="2356" />][5]

（VM内のターミナルを起動して「ifconfig」コマンドを実行できます。このケースでは172.16.156.130です）。その後お使いのMac上で、以下のようにhostsファイルを編集し、

<pre><code class="bash">sudo vi /etc/hosts</pre>

以下のように行を追加します。

<pre><code class="bash">172.16.156.130 quickstart.cloudera</pre>

IPはVMから取得した値です。保存して、先に進む準備は整いました！

**ステップ6：実行！**
  
ターミナルのHueフォルダから行わなければならないことは、単に以下を実行するだけです:

<pre><code class="bash">./build/env/hue runserver</pre>

そして、ブラウザで<http://localhost:8000>を指定します！今すぐ<a>新しいアプリを</a>を書いて下さい！ <img class="wp-smiley" src="https://gethue.com/wp-includes/images/smilies/icon_smile.gif" alt="4。" />

[<img class="aligncenter size-large wp-image-2360" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-13.35.34-1024x716.png" alt="Screenshot 2015-03-23 13.35.34" width="1024" height="716" data-wp-pid="2360" />][6]

&nbsp;

いつものように、いつものように、コメントとフィードバックは [hue-user][7] メーリングリストや[@gethue][8]までお気軽に！

 [1]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.11.26.png
 [2]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-09.09.20.png
 [3]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [4]: https://cdn.gethue.com/uploads/2015/03/pseudo-distributed.ini
 [5]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-24-08.56.33.png
 [6]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-13.35.34.png
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue