---
title: 'Quick Task: How to query Apache Druid analytic database'
author: admin
type: post
date: 2019-03-22T14:54:28+00:00
url: /quick-task-how-to-query-apache-druid-analytic-database/
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
  - Version 4
  # - Version 4.4

---
Self-service exploratory analytics is one of the most common use cases of the Hue users. While deeply integrated with [Apache Impala][1] and [Apache Hive][2], Hue also lets you take advantage of its [smart editor][3] and assistants with any databases. In this tutorial, let's see how to query [Apache Druid][4].

Apache Druid is an "[OLAP style"][5] database.

If not already running, it is easy to get Druid [downloaded][6] and [started][7]. In our case we will just query the provided Wikipedia data sample.


{{< youtube KByeO8AJots >}}


## Administrator

First, let's make sure that Hue can talk to Druid via the [pydruid SqlAlchemy][8] connector. Either make sure it is in the global Python environment via a usual 'pip install' or install it in the Hue virtual environment.

    ./build/env/bin/pip install pydruid

**Note:** Make sure the version is equal or more to 0.4.1 if not you will get a "Can't load plugin: sqlalchemy.dialects:druid".

In the hue.ini configuration file, now let's add the interpreter. Here 'druid-host.com' would be the machine where Druid is running.

    [notebook]
    [[interpreters]]
    [[[druid]]]
    name = Druid
    interface=sqlalchemy
    options='{"url": "druid://druid-host.com:8082/druid/v2/sql/"}'


And now restart Hue.

## User

And that's it, now open-up <http://127.0.0.1:8000/hue/editor/?type=pydruid> (replace host or port of your actual Hue) and you can start querying!

    SELECT countryName, count(*) t
    FROM druid.wikipedia
    GROUP BY countryName
    ORDER BY t DESC
    LIMIT 100

As usual feel free to comment here or to send feedback to the [hue-user][9] list or [@gethue][10]!

[<img src="https://cdn.gethue.com/uploads/2019/03/druid_querying.png"/>][11]

&nbsp;

 [1]: https://impala.apache.org/
 [2]: https://hive.apache.org/
 [3]: http://cloudera.github.io/hue/latest/user/editor/
 [4]: http://druid.io/
 [5]: http://druid.io/docs/latest/design/index.html#what-is-druid
 [6]: http://druid.io/downloads.html
 [7]: http://druid.io/docs/latest/tutorials/index.html
 [8]: https://github.com/druid-io/pydruid
 [9]: http://groups.google.com/a/cloudera.org/group/hue-user
 [10]: https://twitter.com/gethue
 [11]: https://cdn.gethue.com/uploads/2019/03/druid_querying.png
