---
title: 'Season II: 1. Prepare the data for analysis with Pig and Python UDF'
author: admin
type: post
date: 2013-09-05T18:47:00+00:00
url: /hadoop-tutorials-ii-1-prepare-the-data-for-analysis/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/60376973455/hadoop-tutorials-ii-1-prepare-the-data-for-analysis
tumblr_gethue_id:
  - 60376973455
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
  - Tutorial
---

<p id="docs-internal-guid-503f040f-ef67-4b6f-ee8d-c485a06d2c9b">
  Welcome to season 2 of the Hue <a href="https://gethue.com/category/full-tutorial/">video series</a>. In this new chapter we are going to demonstrate how Hue can simplify Hadoop usage and lets you focus on the business and less about the underlying technology. In a real life scenario, we will use various Hadoop tools within the Hue UI and explore some data and extract some competitive advantage insights from it.
</p>

&nbsp;

{{< youtube BVY07kj8nU4 >}}

Let’s go surf the Big Data wave, directly from your Browser!

We want to open a new restaurant. In order to optimize our future business we would like to learn more about the existing restaurants, which tastes are trending, what food eaters are looking for or are positive/negative about… In order to answer these questions, we are going to need some data.

Luckily, Yelp is providing some [datasets][1] of restaurants and reviews and we download them. What’s next? Let’s move the data into Hadoop and make it queryable!

# Convert Json data with Pig

The current format is Json, which is easy to save but difficult to query as it consist in one big record for each row and requires a more sophisticated loader. We are also going to cleanup the data a bit in the process.

In order to do this in a scalable way, we are going to use the query tool [Apache Pig][2] and to make it easy, the [Pig Editor][3] in Hue. We explain two ways to do it.

All the code is available on the [Hadoop Tutorial][4] github.

# Method 1: Pig JsonLoader/JsonStorage

Pig natively provides a [JsonLoader][5]. We load our data and map it to a schema, then explode the votes into 3 columns. Notice the clean-up of the text of the reviews.

Here is the [script][6]:

<pre class="code">reviews =
  LOAD 'yelp_academic_dataset_review.json'
  USING JsonLoader('votes:map[],user_id:chararray,review_id:chararray,stars:int,date:chararray,text:chararray,type:chararray,business_id:chararray');

tabs =
  FOREACH reviews
  GENERATE
     (INT) votes#'funny', (INT) votes#'useful', (INT) votes#'cool', user_id, review_id, stars, REPLACE(REPLACE(text, 'n', ''), 't', ''), date, type, business_id;

STORE tabs INTO 'yelp_academic_dataset_review.tsv';</pre>

&nbsp;

Note: if the script fails with a ClassNotFound exception, you might need to logging as ‘oozie’ or ‘hdfs’ and upload /usr/lib/pig/lib/json-simple-1.1.jar into [/user/oozie/share/lib/pig][7] on HDFS with [File Browser][8].

# Method 2: Pig Python UDF

Let’s convert the business data to TSV with a great Pig features: [Python UDF][9]. We are going to process each row with with a UDF loading the Json records one by one and printing them with tabs as delimiter.

As Pig is currently using Jython 2.5 for executing Python UDF and there is no builtin json lib, we need to download jyson from <http://downloads.xhaus.com/jyson/>. Grab the jyson-1.0.2 version, extract it and upload jyson-1.0.2.jar to /user/oozie/share/lib/pig with FileBrowser.

We need to import our Python UDF into Pig. Open up the Pig Editor and upload a file resource named [converter.py][10]. You can also create the file directly on HDFS with FileBrowser, then edit it and add this [script][6]:

<pre class="code">from com.xhaus.jyson import JysonCodec as json

@outputSchema("business:chararray")
def tsvify(line):
 business_json = json.loads(line)
 business = map(unicode, business_json.values())
 return 't'.join(business).replace('n', ' ').encode('utf-8')</pre>

Go to ‘Properties’, ‘Resource’ and specify the path to converter.py on HDFS.

You are then ready to type the following Pig [script][11]:

<pre class="code">REGISTER 'converter.py' USING jython AS converter;

reviews =
  LOAD '/user/romain/yelp/yelp_academic_dataset_business.json' AS (line:CHARARRAY);

tsv =
  FOREACH reviews
  GENERATE converter.tsvify(line);

STORE tsv INTO 'yelp_academic_dataset_business.tsv'</pre>

#

# What’s next?

Pig is a powerful tool for processing terabytes of data and Hue Pig Editor makes it easier to play around. Python UDF will become part of the editor when [HUE-1136][12] is finished. In episode 3, we will see how to convert to even better formats.

In the [next episode][13], let’s see how to query the data and learn more about the restaurant market!

[1]: http://www.yelp.com/dataset_challenge/
[2]: http://pig.apache.org/
[3]: http://gethue.tumblr.com/post/51559235973/tutorial-apache-pig-editor-in-hue-2-3
[4]: https://github.com/romainr/hadoop-tutorials-examples
[5]: http://pig.apache.org/docs/r0.11.1/func.html#jsonloadstore
[6]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/pig-json-python-udf/clean_json.pig
[7]: http://127.0.0.1:8888/filebrowser/#/user/oozie/share/lib/pig
[8]: http://gethue.tumblr.com/post/48706244836/demo-hdfs-file-operations-made-easy-with-hue
[9]: http://pig.apache.org/docs/r0.11.1/udf.html#python-udfs
[10]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/pig-json-python-udf/converter.py
[11]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/pig-json-python-udf/python_udf.pig
[12]: https://issues.cloudera.org/browse/HUE-1136
[13]: https://gethue.com/hadoop-tutorials-ii-2-execute-hive-queries-and/ 'Season II: 2. Execute Hive queries and schedule them with Oozie'
