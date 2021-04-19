---
title: How to use the Livy Spark REST Job Server API for sharing Spark RDDs and contexts
author: admin
type: post
date: 2015-10-13T11:38:06+00:00
url: /how-to-use-the-livy-spark-rest-job-server-api-for-sharing-spark-rdds-and-contexts/
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
categories:
  - Development

---
<span style="font-weight: 400;">Livy is an </span>[<span style="font-weight: 400;">open source REST interface</span>][1] <span style="font-weight: 400;">for interacting with Apache Spark from anywhere. It supports executing snippets of Python, Scala, R code or programs in a Spark Context that runs locally or in YARN.</span>

<span style="font-weight: 400;">In the episode 1 we previously detailed how to use the <a href="https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/">interactive Shell API</a>.</span>

<span style="font-weight: 400;">In this follow-up, lets put the API in practice for a more concrete example: let's simulate sharing <a href="http://spark.apache.org/docs/latest/quick-start.html">RDDs</a> or contexts!</span>

&nbsp;

## **Starting the REST server**

This is described in the [previous post section][2].

&nbsp;

## **Sharing Spark contexts...**

<span style="font-weight: 400;">Livy offers remote Spark sessions to users. They usually have one each (or one by Notebook):</span>

<pre><code class="bash"># Client 1

curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 + 1"}'

\# Client 2

curl localhost:8998/sessions/1/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'

\# Client 3

curl localhost:8998/sessions/2/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'

</code></pre>

[<img src="https://cdn.gethue.com/uploads/2015/10/livy_shared_contexts2-1024x565.png"  />][3]

&nbsp;

## **... and so sharing RDDs**

If the users were pointing to the same session, they would interact with the same Spark context. This context would itself manages several RDDs. Users simply need to use the same session id, e.g. 0, and issue commands there:

<pre><code class="bash"># Client 1

curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 <a href="https://cdn.gethue.com/uploads/2015/10/livy_multi_contexts.png"><img src="https://cdn.gethue.com/uploads/2015/10/livy_multi_contexts-1024x566.png"  /></a>+ 1"}'

\# Client 2

curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'

\# Client 3

curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}' </code></pre>

[<img src="https://cdn.gethue.com/uploads/2015/10/livy_multi_rdds2-1024x557.png"  />][4]

&nbsp;

## **... Accessing them from anywhere**

Now we can even make it more sophisticated while keeping it simple. Imagine we want to simulate a shared in memory key/value store. One user can start a named RDD on a remote Livy PySpark session and anybody could access it.

[<img src="https://cdn.gethue.com/uploads/2015/10/livy_shared_rdds_anywhere2-1024x557.png"  />][5]

To make it prettier, we can wrap it in a few lines of Python and call it `ShareableRdd`. Then users can directly connect to the session and set or retrieve values.

<pre><code class="python">

class ShareableRdd():

def __init__(self):

self.data = sc.parallelize([])

def get(self, key):

return self.data.filter(lambda row: row[0] == key).take(1)

def set(self, key, value):

new_key = sc.parallelize([[key, value]])

self.data = self.data.union(new_key)

</code></pre>

`set()` adds a value to the shared RDD, while `get()` retrieves it.

<pre><code class="python">

srdd = ShareableRdd()

srdd.set('ak', 'Alaska')

srdd.set('ca', 'California')

</code></pre>

<pre><code class="python">

srdd.get('ak')

</code></pre>

If using the REST Api directly someone can access it with just these commands:

<pre><code class="bash">curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"srdd.get(\"ak\")"}'

{"id":3,"state":"running","output":null}</code></pre>

<pre><code class="bash">curl localhost:8998/sessions/0/statements/3

{"id":3,"state":"available","output":{"status":"ok","execution_count":3,"data":{"text/plain":"[['ak', 'Alaska']]"}}}</code></pre>

We can even get prettier data back, directly in json format by adding the `%json` magic keyword:

<pre><code class="bash">curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"data = srdd.get(\"ak\")\n%json data"}'

{"id":4,"state":"running","output":null}</code></pre>

<pre><code class="bash">curl localhost:8998/sessions/0/statements/4

{"id":4,"state":"available","output":{"status":"ok","execution_count":2,"data":{"application/json":[["ak","Alaska"]]}}}</code></pre>

Note

Support for `%json srdd.get("ak")` is on the way!

&nbsp;

## **Even from any languages**

<span style="font-weight: 400;">As Livy is providing a simple REST Api, we can quickly implement a little wrapper around it to offer the shared RDD functionality in any languages. Let's do it with regular Python:</span>

<pre><code class="python">pip install requests

python</code></pre>

Then in the Python shell just declare the wrapper:

<pre><code class="python">

import requests

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

</code></pre>

Instantiate it and make it point to a live session that contains a `ShareableRdd`:

<pre><code class="python">states = SharedRdd('http://localhost:8998/sessions/0', 'states')

</code></pre>

And just interact with the RDD transparently:

<pre><code class="python">states.get('ak')

states.set('hi', 'Hawaii')

</code></pre>

&nbsp;

<span style="font-weight: 400;">And that's it! This shared RDD example is a good demo of the capabilities of the REST Api and does claim any production support for Shared RDDs. The shared RDD  could also supporting loading, saving... and being discovered through a RDD listing API.</span>

<span style="font-weight: 400;">All the code sample is available on <a href="https://github.com/romainr/hadoop-tutorials-examples/tree/master/notebook/shared_rdd">github</a> and will work with the very latest version of Livy.</span>

<span style="font-weight: 400;">If you want to learn more about the Livy Spark REST Api, feel free to send questions on the <a href="http://groups.google.com/a/cloudera.org/group/hue-user">user list</a> or meet up in person at the upcoming</span> [Spark Summit][6] in Amsterdam!

&nbsp;

 [1]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
 [2]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/#starting
 [3]: https://cdn.gethue.com/uploads/2015/10/livy_shared_contexts2.png
 [4]: https://cdn.gethue.com/uploads/2015/10/livy_multi_rdds2.png
 [5]: https://cdn.gethue.com/uploads/2015/10/livy_shared_rdds_anywhere2.png
 [6]: https://spark-summit.org/eu-2015/events/building-a-rest-job-server-for-interactive-spark-as-a-service/
