---
title: Apache Pig Editor in Hue 2.3
author: admin
type: post
date: 2013-05-28T14:02:00+00:00
url: /tutorial-apache-pig-editor-in-hue-2-3/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/51559235973/tutorial-apache-pig-editor-in-hue-2-3
tumblr_gethue_id:
  - 51559235973
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

In the previous installment of the demo series about [Hue][1] — the open source Web UI that makes [Apache Hadoop][2] easier to use — you learned how to [analyze data with Hue using Apache Hive via Hue’s Beeswax and Catalog applications][3]. In this installment, we’ll focus on using the new editor for [Apache Pig][4] in [Hue 2.3][5].

{{< youtube BVY07kj8nU4 >}}

Complementing the editors for Hive and Cloudera Impala, the Pig editor provides a great starting point for exploration and real-time interaction with Hadoop. This new application lets you edit and run Pig scripts interactively in an editor tailored for a great user experience. Features include:

- UDFs and parameters (with default value) support
- Autocompletion of Pig keywords, aliases, and HDFS paths
- Syntax highlighting
- One-click script submission
- Progress, result, and logs display
- Interactive single-page application

Here’s a short video demoing its capabilities and ease of use:

The demo [data][6] is based on the previous [Hive and Metastore demo][7] and its cleaned business file.

Here is the Pig script used and explained in this demo. It is loading the Yelp business file that was converted in the [previous demo][3] and computing the top-25 most reviewed restaurants:

<pre class="code">business =
	LOAD '/user/hive/warehouse/business/yelp_academic_dataset_business_clean.json'
	AS (business_id: CHARARRAY, categories: CHARARRAY, city: CHARARRAY, full_address: CHARARRAY,
    	latitude: FLOAT, longitude: FLOAT, name: CHARARRAY, neighborhoods: CHARARRAY,
    	open: BOOLEAN, review_count: INT, stars: FLOAT, state: CHARARRAY, type: CHARARRAY);

business_group =
  GROUP business
  BY city;

business_by_city =
  FOREACH business_group
  GENERATE group, COUNT(business) AS ct;

top =
	ORDER business_by_city
	BY ct DESC;

top_25 = LIMIT top 25;

DUMP top_25;</pre>

## What’s Next?

New features like support for [Python UDF][8]s and better integration with Apache Oozie and [File Browser][9] are on the way. As usual, we welcome all [feedback][10]!

[1]: https://gethue.com
[2]: http://hadoop.apache.org/
[3]: http://blog.cloudera.com/blog/2013/04/demo-analyzing-data-with-hue-and-hive/
[4]: http://pig.apache.org/
[5]: https://gethue.com
[6]: https://github.com/romainr/yelp-data-analysis#yelp-data-analysis-with-hue
[7]: http://blog.cloudera.com/2013/04/demo-analyzing-data-with-hue-and-hive/
[8]: https://issues.cloudera.org/browse/HUE-1136
[9]: http://blog.cloudera.com/2013/04/demo-hdfs-file-operations-made-easy-with-hue/
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
