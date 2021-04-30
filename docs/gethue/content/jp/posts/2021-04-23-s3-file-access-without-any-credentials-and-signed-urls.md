---
title: ユーザーに資格情報キーを与えずにS3ファイルへの適切なアクセスを提供する
author: Hue Team
type: post
date: 2021-04-23T00:00:00+00:00
url: /blog/2021-04-23-s3-file-access-without-any-credentials-and-signed-urls/
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

AWS S3 署名付きURLを使用してバケット、キーを一覧表示し、ファイルを管理します。

[SQL クエリ](https://medium.com/data-querying/interactively-querying-hbase-via-sql-273013e5b3cc) は、データをオープンにし、ユーザーが確固たる事実に裏打ちされた意思決定を行うのに役立ちます。 しかし、ユーザーが必要とするデータがデータウェアハウスにまだ存在しない場合はどうでしょうか?

より多くのセルフサービス体験を提供するために、ユーザーは [自分のデータのクエリ](https://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/) や結合を行い、クエリ結果ファイルをエクスポートして共有することができます。

ここでは、 [Hueエディタ](http://gethue.com/) プロジェクトで、署名付きURLが導入された実際のシナリオを紹介します。

![Hueは、HDFS、S3、ADLSのいずれに対しても、同じで一貫したファイル・ブラウジング・インターフェースを提供する](https://cdn-images-1.medium.com/max/2572/1*BMrZbQFTCBM8Ad9eZykaKA.png)
<br>
*Hueは、HDFS、S3、ADLSのいずれに対しても、同じで一貫したファイル・ブラウジング・インターフェースを提供する*

HueのSQLエディタは、 [ファイルブラウザ](https://gethue.com/introducing-s3-support-in-hue/)を介してクラウドストレージへの透過的なアクセスを提供してきました。 S3やADLSのネイティブなWeb UIに直接アクセスすると使いづらく、クラウドに依存しないため、このアプリは非常に人気があります(また、S3やADLSのインターフェイスは、シンプルさと非エンジニア向けに設計されていません)。 さらに、SQLユーザーのほとんどは、同じように見えるHDFSブラウザに慣れています。

しかし、 これは通常S3資格情報キーのセットをHue Serverに提供し、それらを全員で共有する必要があるため、クラスタ管理者にとっては頭痛の種となります。 あまり安全ではありません。 ファイルブラウザを管理者のみに許可すると、機能が制限されてしまい、振り出しに戻ってしまいます。

そこで、 [S3 署名URL](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html) が登場し、この煩わしさを解消してくれます。

![Hue経由でS3とやりとりしているユーザーと共有資格キー(ベストではない)](https://cdn-images-1.medium.com/max/2000/1*l0x18bjmRAOFJBEP_QfEtw.png)
<br>
*Hue経由でS3とやりとりしているユーザーと共有資格キー(ベストではない)*


![ユーザーは、任意のS3リソースにアクセスできる個別の一時的なURLを取得 (安全かつ詳細なアクセスが可能)](https://cdn-images-1.medium.com/max/2000/1*hqkJ2QR1SdLf4Af0Z4ABHw.png)
<br>
*ユーザーは、任意のS3リソースにアクセスできる個別の一時的なURLを取得 (安全かつ詳細なアクセスが可能)*

<br><br> これらのURLは、通常期限が切れる (例: 5分後など) ように設定されており、「署名」されています。これは、ユーザーが自動的に向こうにならないように変更できないため、ユーザーに対して公開しても安全です。

もう1つの利点は、Hue Web ServerがS3の資格情報を持つ必要がないことです。 Hueは、この例では、ユーザーが行いたいS3コールに相当するURLを提供するように、 [RAZ Server](https://blog.cloudera.com/access-control-for-azure-adls-cloud-object-storage/) に要求するだけです。

![以前(上) では、AWS Python SDK を直接呼び出してバケットのリストを取得し、それぞれのバケットを表すPythonオブジェクトを取得しなおしています。 以降(下）では、特別なURLを要求して、追加の認証なしにS3に直接HTTPリクエストを行い、XMLデータを取得しています。](https://cdn-images-1.medium.com/max/2000/1*hXFR_nN5biT1aawJfTVqew.png)
<br>
*以前(上) では、AWS Python SDK を直接呼び出してバケットのリストを取得し、それぞれのバケットを表すPythonオブジェクトを取得しなおしています。 以降(下）では、特別なURLを要求して、追加の認証なしにS3に直接HTTPリクエストを行い、XMLデータを取得しています。*

<hr />

このセクションでは、内部の実装について詳しく説明し、より多くの開発者をターゲットにしています。

![ネイティブ (Boto) と署名されたURL (RAZ) のアクセスパスをより詳細に説明します。 最も重要なのは、署名付き URL を要求または生成するにはBoto S3 クラスをオーバーライドする必要があり、Boto ライブラリですべてを行うのではなく、HTTP コールを行う必要があることです。 S3クレデンシャルキーはなくなり、S3接続オブジェクトも使用されません。(これを保証するためにNoneに設定されています)。](https://cdn-images-1.medium.com/max/3000/1*C8dNjZ_iC3Lk7TMsF2Oy3w.png)
<br>
*ネイティブ (Boto) と署名付きURL (RAZ) のアクセスパスをより詳細に説明します。 最も重要なのは、署名付き URL を要求または生成するにはBoto S3 クラスをオーバーライドする必要があり、Boto ライブラリですべてを行うのではなく、HTTP コールを行う必要があることです。 S3クレデンシャルキーはなくなり、S3接続オブジェクトも使用されません。(これを保証するためにNoneに設定されています)。*

マジックピースの1つはRAZサーバーで、S3コールを署名付きURLに変換することができます。 RAZ はまた、 [Apache Ranger](https://ranger.apache.org/) を活用しており、認可と細かいパーミッションを提供しています。(つまり、誰がこのバケットにアクセスできるのか、 誰がこのディレクトリにファイルをアップロードできるのか)

RAZはオープンソースではありませんが、URL生成の基本的なロジックは以下のようになっています。

ここでは、「バケットの一覧」のような呼び出しを、署名付きのS3のURLで置き換える方法をデモしたコードの一部を紹介します。

* Boto3: [create_presigned_url()](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)
* Boto2: [generate_url()](http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.connection.S3Connection.generate_url), 例: connection.generate_url(3600, ‘GET’)

そして、それを呼び出し、XML を Python オブジェクトにアンマーシャルで戻す方法です。

    import boto
    import xml.sax
    import requests
    
    from boto.resultset import ResultSet
    from boto.s3.bucket import Bucket
    
    tmp_url = 'https://s3-us-west-1.amazonaws.com/?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA23E77ZX2HVY76YGL%2F20210422%2Fus-west-1%2Fs3%2Faws4_request&X-Amz-Date=20210422T213700Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=2efc90228ec9255636de27dab661e071a931f0aea7b51a09027f4747d0a78f6e'
    
    response = requests.get(tmp_url)
    
    print(response)
    
    rs = ResultSet([('Bucket', Bucket)])
    h = boto.handler.XmlHandler(rs, None)
    xml.sax.parseString(response.content, h)
    
    print(rs)
    print([k for k in rs[0].list(prefix='data/')])

これにより、ネイティブのBotoを使用している場合と同じバケットオブジェクトが表示されます。

    > <Response [200]>
    [<Bucket: demo-gethue>, <Bucket: gethue-test>]

![全体像：主に左側には、Hue File System ライブラリがあります。これは、あらゆるストレージシステム(HDFS、S3ネイティブ、S3 via Signed URL、ADLS...) に対してファイルブラウジングを提供するための汎用的なものです。 右側では、呼び出しごとに署名付き URL を生成できるサービスと相互作用するクライアントを構築する方法についてです](https://cdn-images-1.medium.com/max/3448/1*PZduhj0fHrxw-PVlue8aeA.png)*全体像：主に左側には、Hue File System ライブラリがあります。これは、あらゆるストレージシステム(HDFS、S3ネイティブ、S3 via Signed URL、ADLS...) に対してファイルブラウジングを提供するための汎用的なものです。 右側では、呼び出しごとに署名付き URL を生成できるサービスと相互作用するクライアントを構築する方法についてです*

確かに複雑に見えますが、クラウドの世界で真のセルフサービスクエリを提供するには、少なくとも1つのピースが解明されなければなりません :)

Hueは [オープンソース](https://github.com/cloudera/hue/) であり、この機能は次の4.10リリースに搭載される予定です。

それでは、皆さんにデータクエリーを楽しんでいただきたいと思います！

Romain from the Hue Team
