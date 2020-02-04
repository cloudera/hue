---
title: SparkのRDDとcontextを共有するために Livy Spark REST Job Server APIを使用する方法
author: Hue Team
type: post
date: 2016-02-12T09:23:06+00:00
url: /how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/
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
  - Livyは任意の場所からApache Sparkを使用するためのオープンソースのRESTインターフェースです。LivyはローカルまたはYARNで実行される、Spark ContextのPython, Scala, Rのコード、あるいはプログラムのスニペットの実行をサポートしています。
categories:
  - Hue 3.10
  - Programming
  - Spark
  - Tutorial

---
（元のブログ記事は<a href="https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/" target="_blank">こちら</a>です）

Livyは任意の場所からApache Sparkを使用するためのオープンソースのRESTインターフェースです。LivyはローカルまたはYARNで実行される、Spark ContextのPython, Scala, Rのコード、あるいはプログラムのスニペットの実行をサポートしています。

エピソード1では、[対話的なシェルAPI][1]の使用方法を以前に説明しました 。

このフォローアップでは、より具体的な例のために実際のAPIを置いてみます：[RDD][2]またはコンテキストの共有をシミュレートしてみましょう！

&nbsp;

## **RESTサーバを起動する**

これは[以前の記事のセクション][3]に記載されています 。

&nbsp;

## **Spark Contextを共有する&#8230;**

<span style="font-weight: 400;">LivyはユーザーにリモートのSparkセッションを提供しています。Sparkのセッションは通常それぞれ（またはノートブックずつ）に一つあります:</span>

<pre><code class="bash"># Client 1
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 + 1"}'
# Client 2
curl localhost:8998/sessions/1/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'
# Client 3
curl localhost:8998/sessions/2/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'
</pre>

[<img class="aligncenter size-large wp-image-3347" src="https://cdn.gethue.com/uploads/2015/10/livy_shared_contexts2-1024x565.png" alt="livy_shared_contexts2" width="1024" height="565" data-wp-pid="3347" />][4]

## **&#8230;なので、RDDを共有する**

ユーザーが同じセッションを指していた場合、それらは同じSpark Contextで相互作用します。このコンテキストはそれ自身がいくつかのRDDを管理するでしょう。ユーザーは単純に同じセッションID、例えば0を使用してこれらのコマンドを発行する必要があります：

<pre><code class="bash"># Client 1
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 &amp;lt;a href="https://cdn.gethue.com/uploads/2015/10/livy_multi_contexts.png"&amp;gt;&amp;lt;img class="aligncenter size-large wp-image-3340" src="https://cdn.gethue.com/uploads/2015/10/livy_multi_contexts-1024x566.png" alt="livy_multi_contexts" width="1024" height="566" data-wp-pid="3340" /&amp;gt;&amp;lt;/a&amp;gt;+ 1"}'
# Client 2
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'
# Client 3
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}' </pre>

[<img class="aligncenter size-large wp-image-3348" src="https://cdn.gethue.com/uploads/2015/10/livy_multi_rdds2-1024x557.png" alt="livy_multi_rdds2" width="1024" height="557" data-wp-pid="3348" />][5]

&nbsp;

## **&#8230;どこからでもアクセス**

これで、シンプルに保ちながら、より洗練させることができます。メモリ内で共有されたキー/バリューストアをシミュレートしたい、と想像してみてください。あるユーザーはリモートのLivy PySparkセッションで名前を付けたRDDを開始することができ、誰もがそこにアクセスできます。

[<img class="aligncenter size-large wp-image-3349" src="https://cdn.gethue.com/uploads/2015/10/livy_shared_rdds_anywhere2-1024x557.png" alt="livy_shared_rdds_anywhere2" width="1024" height="557" data-wp-pid="3349" />][6]

よりきれいに見せるため、それを数行のPythonでラップして`ShareableRdd`で呼び出すことができます 。その後、ユーザーは直接セッションに接続して値をセット、あるいは取得できます。

<pre><code class="python">class ShareableRdd():

def __init__(self):
self.data = sc.parallelize([])

def get(self, key):
return self.data.filter(lambda row: row[0] == key).take(1)

def set(self, key, value):
new_key = sc.parallelize([[key, value]])
self.data = self.data.union(new_key)
</pre>

`set()`はshared RDDに値を追加し`get()`で取得します。

<pre><code class="python">srdd = ShareableRdd()

srdd.set('ak', 'Alaska')
srdd.set('ca', 'California')
</pre>

<pre><code class="python">srdd.get('ak')
</pre>

REST APIを直接使用している場合、単にこれらのコマンドでアクセスすることができます。

<pre><code class="bash">curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"srdd.get(\"ak\")"}'
{"id":3,"state":"running","output":null}</pre>

<pre><code class="bash">curl localhost:8998/sessions/0/statements/3
{"id":3,"state":"available","output":{"status":"ok","execution_count":3,"data":{"text/plain":"[['ak', 'Alaska']]"}}}</pre>

`%json`マジックキーワードを追加することにより、戻ってくるデータを直接JSON形式できれいに取得することさえもできます：

<pre><code class="bash">curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"data = srdd.get(\"ak\")\n%json data"}'
{"id":4,"state":"running","output":null}</pre>

<pre><code class="bash">curl localhost:8998/sessions/0/statements/4
{"id":4,"state":"available","output":{"status":"ok","execution_count":2,"data":{"application/json":[["ak","Alaska"]]}}}</pre>

注意
  
`%json srdd.get("ak")`の対応は道半ばです！

&nbsp;

## **任意の言語からでも**

LivyはシンプルなREST APIを提供しているので、任意の言語でのshared RDDの機能を提供するために、その周辺に少しのラッパーを素早く実装することができます。では通常のPythonでやってみましょう：

<div class="syntaxhighlighter python">
</div>

<div class="syntaxhighlighter python">
</div>

<pre><code class="python">pip install requests
python</pre>

<div class="syntaxhighlighter python">
  そして、Pythonシェルで単なるラッパーを宣言します。
</div>

<pre><code class="python">import requests
import json

class SharedRdd():
"""
Perform REST calls to a remote PySpark shell containing a Shared named RDD.
"""
def __init__(self, session_url, name):
self.session_url = session_url
self.name = name

def get(self, key):
return self._curl('%(rdd)s.get("%(key)s")' % {'rdd': self.name, 'key': key})

def set(self, key, value):
return self._curl('%(rdd)s.set("%(key)s", "%(value)s")' % {'rdd': self.name, 'key': key, 'value': value})

def _curl(self, code):
statements_url = self.session_url + '/statements'
data = {'code': code}
r = requests.post(statements_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
resp = r.json()
statement_id = str(resp['id'])
while resp['state'] == 'running':
r = requests.get(statements_url + '/' + statement_id)
resp = r.json()
return r.json()['data']
</pre>

インスタンス化して`ShareableRdd`を含んだライブセッションを指すようにします ：

<pre><code class="python">states = SharedRdd('http://localhost:8998/sessions/0', 'states')
</pre>

そして、RDDと透過的にやりとりします。

<pre><code class="python">states.get('ak')
states.set('hi', 'Hawaii')
</pre>

これです！この共有したRDDの例はREST APIの機能の優れたデモで、どの製品も共有されたRDDをサポートする主張しています。共有されたRDDは、ロード、保存、RDDのリストAPIを介しての探索もサポートできます。

すべてのコードの例は[github][7]で利用可能で、Livyの最新版で動作します。

Livy Spark REST APIについてさらに学習したい方はユーザーリストやアムステルダムの[Spark Summit][8]で気軽に直接質問を送ってください。！

 [1]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/
 [2]: http://spark.apache.org/docs/latest/quick-start.html
 [3]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/#starting
 [4]: https://cdn.gethue.com/uploads/2015/10/livy_shared_contexts2.png
 [5]: https://cdn.gethue.com/uploads/2015/10/livy_multi_rdds2.png
 [6]: https://cdn.gethue.com/uploads/2015/10/livy_shared_rdds_anywhere2.png
 [7]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/notebook/shared_rdd
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user