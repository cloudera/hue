---
title: HueでのAmazon S3サポートの紹介
author: Hue Team
type: post
date: 2016-08-25T14:47:45+00:00
url: /introducing-s3-support-in-hue/
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
  - 私たちはHue 3.11 リリース での HueとAmazon S3 （Amazon Simple Storage Service) の統合の正式な紹介ができることに非常に興奮しています。Hueは 設定されたS3アカウントに読み書きするようにセットアップでき、ユーザはHDFSに中間データとして移動/コピーせず、S3に直接問い合わせを行い、データをS3に保存できます。
categories:
  - File Browser
  - Hue 3.11
  - Metastore

---
<p class="p1">
  私たちは<a href="https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/">Hue 3.11 リリース</a> での Hueと<a href="https://aws.amazon.com/s3/">Amazon S3</a> （Amazon Simple Storage Service) の統合の正式な紹介ができることに非常に興奮しています。Hueは 設定されたS3アカウントに読み書きするようにセットアップでき、ユーザはHDFSに中間データとして移動/コピーせず、S3に直接問い合わせを行い、データをS3に保存できます。
</p>

## HueにおけるS3の設定 {.p3}

<p class="p1">
  Hueのファイルブラウザは、HDFSに加えて、ユーザーがS3アカウントでデータを探索、管理、アップロードできるようになりました。
</p>

<p class="p1">
  HueにS3のアカウントを追加するには、アクセスキーIDとシークレットアクセスキーを含め、有効なS3の資格情報を使用してHueを設定する必要があります。 <a href="http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html"><span class="s1">http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/ AWSCredentials.html</span></a>
</p>

<p class="p1">
  これらのキーは、Hueによって読み込まれる、実際のアクセスキーと秘密鍵を標準出力に出力するスクリプト内にセキュアに保存できます。（これはどのように<a href="https://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/">Hueがパスワードのスクリプトを読み込む</a>かに似ています。スクリプトファイルを使用するためには、<code>hue.ini</code>設定ファイルに次のセクションを追加します：
</p>

<pre><code class="bash">[aws]
[[aws_accounts]]
[[[default]]]
access_key_id_script=/path/to/access_key_script
secret_access_key_script= /path/to/secret_key_script
allow_environment_credentials=false
region=us-east-1
</pre>

<p class="p1">
  あるいは（本番環境やセキュア環境では推奨しませんが）、<code>access_key_id</code>と<code>secret_access_key</code>を、あなたのキーをプレーンテキストで値を設定できます：
</p>

<pre><code class="bash">[aws]
[[aws_accounts]]
[[[default]]]
access_key_id=s3accesskeyid
secret_access_key=s3secretaccesskey
allow_environment_credentials=false
region=us-east-1
</pre>

<p class="p1">
  このリージョンは、S3アカウントに対応したAWSのリージョンに設定する必要があります。 デフォルトでは、リージョンは &#8216;us-east-1&#8217;に設定されます
</p>

### HadoopとS3の統合 {.p3}

<p class="p1">
  S3の資格情報でHueを設定することに加えて、S3から読み出してS3に保存するには、HadoopもS3認証資格情報で設定する必要があります。 これは<code>core-site.xml</code>ファイルに次のプロパティを設定することによって行うことができます：
</p>

<pre><code class="xml">&lt;property&gt;
  &lt;name&gt;fs.s3a.awsAccessKeyId&lt;/name&gt;
  &lt;value&gt;AWS access key ID&lt;/value&gt;
&lt;/property/&gt;

&lt;property&gt;
  &lt;name&gt;fs.s3a.awsSecretAccessKey&lt;/name&gt;
  &lt;value&gt;AWS secret key&lt;/value&gt;
&lt;/property/&gt;
</pre>

<p class="p4">
  <span class="s2">詳細については<a href="http://wiki.apache.org/hadoop/AmazonS3"><span class="s1">http://wiki.apache.org/hadoop/AmazonS3</span></a>を参照してください</span>
</p>

<p class="p1">
  navigation:HueとHadoopを設定し、Hueを再起動して設定ページを確認することで、HueがS3アカウントに正常に接続できることが確認できます。また、メインナビゲーションのファイルブラウザメニューにドロップダウンオプションが追加されていることがわかるでしょう
</p>

[<img class="aligncenter size-large wp-image-4397" src="https://cdn.gethue.com/uploads/2016/08/s3_configuration-1024x559.png" alt="Hue S3 Configuration" width="1024" height="559" data-wp-pid="4397" />][1]

##  {.p3}

## HueのファイルブラウザでS3を探索する {.p3}

<p class="p1">
  HueがS3に接続するように構成されると、S3のルート(root)をクリックすることでアカウント内のアクセス可能なすべてのバケットを表示できます。
</p>

<p class="p1">
  ユーザーは、このビューから新しいバケットを作成したり、既存のバケットを削除することもできます。
</p>

#### 注：一意のバケット名

❗️ S3バケット名は、 _すべてのリージョン_で一意である必要があります 。予約した名前でバケットを作成または名前を変更しようとすると、Hueがエラーになります。

<p class="p1">
  ただし、ほとんどの場合、ユーザーはバケット内のキーを使用して直接作業します。バケット・ビューから、ユーザーはバケットをクリックしてそのコンテンツを展開することができます。 ここから、既存のキー（ディレクトリとファイルの両方）を表示したり、既存のディレクトリやファイルを作成、名前変更、移動、コピー、または削除することができます。さらに、S3にファイルを直接アップロードすることもできます
</p>

<img class="aligncenter size-large wp-image-4398" alt="S3 in Filebrowser" width="1258" height="693" data-gifffer="https://cdn.gethue.com/uploads/2016/08/s3_filebrowser.gif" data-wp-pid="4398" />

## S3から直接Hiveテーブルを作成する {.p3}

HueのMetastore Import Data Wizardは、S3のデータディレクトリから外部のHiveテーブルを直接作成できます。これは、HDFSまたはHive Warehouseにデータを移動またはコピーすることなく、[HiveやImpalaからSQL][2]を介してS3のデータを照会することができます。

S3から外部のHiveテーブルを作成するには、Metastoreアプリケーションに移動し、目的のデータベースを選択し、右上の「ファイルから新しいテーブルを作成する」アイコンをクリックします。

テーブル名とオプションの説明を入力し、 &#8220;入力ファイルまたはディレクトリ&#8221;ファイルピッカーでS3Aファイルシステムを選択し、目的のデータファイルを含む親ディレクトリに移動し、 &#8220;このフォルダを選択&#8221;ボタンをクリックします。[Load Data (データの読み込み)]ドロップダウンでは、このテーブルが外部データディレクトリを直接参照することを示す[Create External Table(外部テーブルの作成)]オプションが自動的に選択されます。

入力ファイルの区切り文字と列定義オプションを選択し、最後にHiveテーブルを作成する準備が整ったら「Create Table(テーブルの作成)」をクリックします。作成すると、新しく作成されたテーブルの詳細がMetastoreに表示されます

<img class="aligncenter size-large wp-image-4399" alt="Hive Table from S3" width="1258" height="693" data-gifffer="https://cdn.gethue.com/uploads/2016/08/s3_metastore.gif" data-wp-pid="4399" />

## クエリ結果をS3に保存 {.p3}

S3データから作成された外部Hiveテーブルを作成したので、HiveまたはImpalaエディタにジャンプしてS3からシームレスに直接データのクエリを開始できます。これらのクエリはS3、HDFSのいずれか、またはその両方が背後にあるテーブルとオブジェクトとを結合できます。クエリ結果はS3に簡単に保存できます。

<img class="aligncenter size-large wp-image-4400" alt="Query S3 Data and Save" width="1258" height="693" data-gifffer="https://cdn.gethue.com/uploads/2016/08/s3_query_and_save.gif" data-wp-pid="4400" />

#### ヒント：ImpalaとS3

? ImpalaとS3とのさらなる高度なユースケースはこちらをご覧ください：[Analytics and BI on Amazon S3 with Apache Impala (Incubating)][3]

## さて、次は {.p3}

追加のファイルシステムとして、Hue 3.11でのS3に対するシームレスなサポートは、クラウドにおけるデータの柔軟性と移植性を向上させる長期的なロードマップの始まりに過ぎません。HDFS、S3、および追加のファイルシステム間の緊密な統合を実現するオブジェクトストアから直接のファイル転送、実行、およびクエリのスケジュールなどの将来の拡張機能にご期待ください。

As always, if you have any questions, feel free to comment here or on the [hue-user list][4] or [@gethue][5]!いつものように、コメントとフィードバックは [hue-user][4] メーリングリストや[@gethue][5]までお気軽に！

 [1]: https://cdn.gethue.com/uploads/2016/08/s3_configuration.png
 [2]: https://gethue.com/sql-editor/
 [3]: http://blog.cloudera.com/blog/2016/08/analytics-and-bi-on-amazon-s3-with-apache-impala-incubating/
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue