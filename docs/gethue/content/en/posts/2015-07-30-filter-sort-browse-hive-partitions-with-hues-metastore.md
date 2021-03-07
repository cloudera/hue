---
title: Filter, Sort and Browse Hive Partitions with Hue’s Metastore App
author: admin
type: post
date: 2015-07-30T20:09:39+00:00
url: /filter-sort-browse-hive-partitions-with-hues-metastore/
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
---

With the latest Hue release, the metastore offers better controls over partitioned Hive tables. Partitioning Hive tables is a great strategy to [improve query performance][1] for Hive-managed tables by avoiding full-table scans.

However, partitioning is also useful for external tables where the data may already reside in HDFS or be managed by a service other than Hive. In these cases, the partition location may not conform to the default dynamic Hive partition location (which takes the table's base location and appends a name=value path token for each partition), and can take any valid data path as the location for the partition.

Take for example an external table called "blog" created with the following partition scheme:

<pre><code class="sql">

CREATE TABLE blog (title STRING, body STRING, pubdate DATE) PARTITIONED BY (dy STRING, dm STRING, dd STRING, dh STRING);

</code></pre>

We can continue to alter the table as needed to add data at specific partition locations:

<pre><code class="sql">

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-01', dh='2015-01-01 00') LOCATION '/user/jennykim/2015/01/01/00';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-01', dh='2015-01-01 12') LOCATION '/user/jennykim/2015/01/01/12';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-02', dh='2015-01-02 00') LOCATION '/user/jennykim/2015/01/02/00';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-02', dh='2015-01-02 12') LOCATION '/user/jennykim/2015/01/02/12';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-03', dh='2015-01-03 00') LOCATION '/user/jennykim/2015/01/03/00';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-03', dh='2015-01-03 12') LOCATION '/user/jennykim/2015/01/03/12';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-04', dh='2015-01-04 00') LOCATION '/user/jennykim/2015/01/04/00';

ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-04', dh='2015-01-04 12') LOCATION '/user/jennykim/2015/01/04/12';

</code></pre>

Regardless of a table's partition locations, Hue's metastore now enables you to browse all the partitions in the table, by clicking the "Show Partitions" link from the table view. By default, the partitions view will sort the partitions in reverse order by name (or newest first, if partitioned by date) and display the first 250 partitions.

If you're searching for a specific set of partitions however, you can now filter on a partition value by clicking the "Add a filter" link, selecting and specifying the filter parameter, then clicking the "Filter" button! Note that multiple partition filters can be added as needed to refine your query, and you can also disable the default sort order to retrieve partition results in alphabetically ascending order.

{{< youtube phkigNhDzuE >}}

[Filter, Sort and Browse Hive Partitions with Hue’s Metastore][2] from [The Hue Team][3] on [Youtube][4].

Finally, you can view the data files in any partition by clicking the "View Partition Files" link which will take you to the filebrowser for that partition's location.

[<img src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21-1024x224.png" />][5]

[<img src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.43.48-1024x564.png" />][6]

Hue offers the flexibility to seamlessly work with your Hive data as-is. Feel free to comment on the [hue-user][7] list or [@gethue][8]!

[1]: http://blog.cloudera.com/blog/2014/08/improving-query-performance-using-partitioning-in-apache-hive/
[2]: https://youtube.com//watch?v=phkigNhDzuE
[3]: https://www.youtube.com/channel/UCTuTkR-hLNN59uqT9bqIa_Q
[4]: https://youtube.com
[5]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21.png
[6]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.43.48.png
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
