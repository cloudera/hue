---
title: Analyzing Data with Hue and Hive
author: admin
type: post
date: 2013-03-11T04:00:00+00:00
url: /tutorial-analyzing-data-with-hue-and-hive/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/48706295801/tutorial-analyzing-data-with-hue-and-hive
tumblr_gethue_id:
  - 48706295801
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
slide_template:
  - default
categories:
---

In the first installment of the demo series about [Hue][1] — the open source Web UI that makes [Apache Hadoop][2] easier to use — you learned how file operations are simplified via the File Browser application. In this installment, we’ll focus on analyzing data with Hue, using Apache Hive via Hue’s Beeswax and Catalog applications (based on [Hue 2.3][3] and later).

{{< youtube RxT0M8JgvOk >}}

The [Yelp Dataset Challenge][4] provides a good use case. This post explains, through a video and tutorial, how you can get started doing some analysis and exploration of Yelp data with Hue. The goal is to find the coolest restaurants in Phoenix!

### Dataset Challenge with Hue

The demo below demonstrates how the “business” and “review” datasets are cleaned and then converted to a Hive table before being queried with SQL.

Now, let’s step through a tutorial based on this demo. The queries and scripts are available on [GitHub][5].

### Getting Started & Normalization

First, get the dataset from the [Yelp Challenge webpage][6]. Then, clean the data using [this script][7].

1. Retrieve the data and extract it. <pre class="code">tar -xvf yelp_phoenix_academic_dataset.tar

cd yelp_phoenix_academic_dataset
wget <a href="https://raw.github.com/romainr/yelp-data-analysis/master/convert.py">https://raw.github.com/romainr/yelp-data-analysis/master/convert.py</a>

yelp_phoenix_academic_dataset\$ ls
convert.py notes.txt READ_FIRST-Phoenix_Academic_Dataset_Agreement-3-11-13.pdf yelp_academic_dataset_business.json yelp_academic_dataset_checkin.json yelp_academic_dataset_review.json yelp_academic_dataset_user.json</pre>

2. Convert it to TSV. <pre class="code">chmod +x convert.py
   ./convert.py</pre>


    &nbsp;</li>

      * The following column headers will be printed by the above script. <pre class="code">["city", "review_count", "name", "neighborhoods", "type", "business_id", "full_address", "state", "longitude", "stars", "latitude", "open", "categories"]

["funny", "useful", "cool", "user_id", "review_id", "text", "business_id", "stars", "date", "type"]</pre></ol>

    ### Create the Tables

    Next, create the Hive tables with the “Create a new table from a file” screen in the Catalog app or Beeswax “Tables” tab.

    [<img title="hue1" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue1.png"/>][8]

    <p class="center-align">
      <strong>Creating a new table</strong>
    </p>

    Upload the data files yelp_academic_dataset_business_clean.json and yelp_academic_dataset_review_clean.json. Hue will then guess the tab separator and then lets you name each column of the tables. (Tip: in Hue 2.3, you can paste the column names in directly.)

    [<img title="hue2" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue2.png"/>][9]

    <p class="center-align">
      <strong>Naming columns</strong>
    </p>

    You can then see the table and browse it.

    [<img title="hue3" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue3.png"/>][10]

    <p class="center-align">
      <strong>Browsing the table</strong>
    </p>

    ### Queries

    Open up Hue’s Hive editor (Beeswax) and run one of these queries:

    **Top 25: business with most of the reviews**

    <pre><code class="sql">
    SELECT name, review_count
    FROM business
    ORDER BY review_count DESC
    LIMIT 25
    {{ < /highlight >}}

    **Top 25: coolest restaurants**

    <pre><code class="sql">SELECT r.review_id, name, SUM(cool) AS coolness

    FROM review r JOIN business b

    ON (r.review_id = b.id)

    WHERE categories LIKE '%Restaurants%'

    GROUP BY r.review_id, name

    ORDER BY coolness DESC

    LIMIT 25

    </code></pre>

    [<img title="hue4" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue4.png"/>][11]

    <p class="center-align">
      <strong>Query editor with SQL syntax highlighting and auto-complete<br /> </strong>
    </p>

    [<img title="hue5" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue5.png"/>][12]

    <p class="center-align">
      <strong>Watch the query runs<br /> </strong>
    </p>

    [<img title="hue6" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue61.png"/>][13]

    <p class="center-align">
      <strong>See the results with an infinite scroll</strong>
    </p>

    Now let your imagination run wild and execute some of your own queries!

    Note: This demo is about doing some quick data analytics and exploration. Running more machine learning oriented jobs like the [Yelp Examples][14] would deserve a separate blog post on how to run [MrJob][15]. Hue users would need to create an Apache Oozie workflow with a Shell action (see below). Notice that a ‘mapred’ user would need to be created first in the User Admin.

    [<img title="hue7" src="http://www.cloudera.com/wp-content/uploads/2013/04/hue71.png"/>][16]

    <p class="center-align">
      <strong>Running MrJob Wordcount example in the Oozie app with a Shell action</strong>
    </p>

    ### What’s Next

    As you can see, getting started with data analysis is simple with the interactive Hive query editor and Table browser in Hue.

    Moreover, all the `SELECT` queries can also be performed in Hue’s Cloudera [Impala][17] application for a real-time experience. Obviously, you would need more data than the sample for doing a fair comparison but the improved interactivity is noticeable.

    In upcoming episodes, you’ll see how to use Apache Pig for doing a similar data analysis, and how Oozie can glue everything together in schedulable workflows.

    Thank you for watching and hurry up, only one month before the end of the [Yelp contest][6]!

[1]: https://gethue.com
[2]: http://hadoop.apache.org/
[3]: https://gethue.com
[4]: http://www.yelp.com/dataset_challenge/
[5]: https://github.com/romainr/yelp-data-analysis
[6]: https://www.yelp.com/dataset_challenge/
[7]: https://github.com/romainr/yelp-data-analysis/blob/master/convert.py
[8]: http://www.cloudera.com/wp-content/uploads/2013/04/hue1.png
[9]: http://www.cloudera.com/wp-content/uploads/2013/04/hue2.png
[10]: http://www.cloudera.com/wp-content/uploads/2013/04/hue3.png
[11]: http://www.cloudera.com/wp-content/uploads/2013/04/hue4.png
[12]: http://www.cloudera.com/wp-content/uploads/2013/04/hue5.png
[13]: http://www.cloudera.com/wp-content/uploads/2013/04/hue61.png
[14]: https://github.com/Yelp/dataset-examples
[15]: https://github.com/Yelp/mrjob
[16]: http://www.cloudera.com/wp-content/uploads/2013/04/hue71.png
[17]: http://www.cloudera.com/content/cloudera/en/products/cloudera-enterprise-core/cloudera-enterprise-RTQ.html
