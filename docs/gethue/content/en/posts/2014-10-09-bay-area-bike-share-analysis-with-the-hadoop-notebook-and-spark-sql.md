---
title: 'Bay Area bike share analysis with the Hadoop Notebook and Spark & SQL'
author: admin
type: post
date: 2014-10-09T16:59:13+00:00
url: /bay-area-bike-share-analysis-with-the-hadoop-notebook-and-spark-sql/
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
  - Tutorial
---

_This post was initially published on the Hue project blog <https://gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2/>_

Apache Spark is [getting popular][1] and Hue contributors are working on making it accessible to even more users. Specifically, by creating a Web interface that allows anyone with a browser to type some Spark code and execute it. A [Spark submission REST API][2] was built for this purpose and can also be leveraged by the developers.

[In a previous post][3], we demonstrated how to use Hue's Search app to seamlessly index and visualize trip data from Bay Area Bike Share and leverage Spark to supplement that analysis by adding weather data to our dashboard.

In this tutorial, we'll use the [Hadoop Notebook][4] to study deeper the peak usage of the Bay Area Bike Share (BABS) system.

To start, download the latest data set from <http://www.bayareabikeshare.com/datachallenge>. This post uses the data from August 2013 through February 2014.

{{< youtube BaTfXqAidiw >}}

## Importing CSV Data with the Metastore App

The BABS data set contains 4 CSVs that contain data for stations, trips, rebalancing (availability), and weather. Using Hue's Metastore [import wizard][5], we can easily import these data sets and create tables that infer their schema from the CSV header.

[<img class="aligncenter wp-image-3105 " src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.00-e1443110873104-1024x503.png" />][6]

[<img src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.54-1024x570.png" />][7]

The import wizard also provides the opportunity to override any field names or types, which we'll do for the Trip data to change the "duration" field from a TINYINT to an INT.

[<img src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.47.22-1024x570.png" />][8]

## Interactive Analysis with an Hadoop Notebook

### Lightning-Fast Impala Queries

Now that we've imported the data into our cluster, we can create a new Notebook to perform our data crunching. To start, we'll run some quick exploration queries using Impala.

Let's find the top 10 most popular start stations based on the trip data:

<pre><code class="sql">SELECT startterminal, startstation, COUNT(1) AS count FROM bikeshare.trips GROUP BY startterminal, startstation ORDER BY count DESC LIMIT 10</code></pre>

[<img src="https://cdn.gethue.com/uploads/2015/09/impala_query-1024x339.png"  />][9]

Once our results are returned, we can easily visualize this data; a bar graph works nicely for a simple COUNT..GROUP BY query.

[<img src="https://cdn.gethue.com/uploads/2015/08/impala_bar_graph-e1443111918854-1024x171.png" />][10]

It seems that the San Francisco Caltrain (Townsend at 4th) was by far the most common start station. Let's determine which end stations, for trips starting from the SF Caltrain Townsend station, were the most popular. We'll fetch the latitude and longitude coordinates so that we can visualize the results on a map.

<pre><code class="sql">

SELECT

s.station_id,

s.name,

s.lat,

s.long,

COUNT(1) AS count

FROM \`bikeshare\`.\`trips\` t

JOIN \`bikeshare\`.\`stations\` s ON s.station_id = t.endterminal

WHERE t.startterminal = 70

GROUP BY s.station_id, s.name, s.lat, s.long

ORDER BY count DESC LIMIT 10

</code></pre>

[<img src="https://cdn.gethue.com/uploads/2015/08/impala_map-e1443111522857-1024x223.png" />][11]

The map visualization indicates that the most popular trips starting from the SF Caltrain station are in fairly close proximity to the station, with most of the destinations being clustered around the Financial District and SOMA.

### Long Running Queries with Hive

For longer-running SQL queries, or queries that require use of Hive's built-in functions, we can add a Hive snippet to our notebook to perform this analysis.

Let's say we wanted to dig further into the trip data for the SF Caltrain station and find the total number of trips and average duration (in minutes) of those trips, grouped by hour.

Since the trip data stores startdate as a STRING, we'll need to apply some string-manipulation to extract the hour within an inline SQL query. The outer query will aggregate the count of trips and the average duration.

<pre><code class="sql">

SELECT

hour,

COUNT(1) AS trips,

ROUND(AVG(duration) / 60) AS avg_duration

FROM (

SELECT

CAST(SPLIT(SPLIT(t.startdate, ' ')[1], ':')[0] AS INT) AS hour,

t.duration AS duration

FROM \`bikeshare\`.\`trips\` t

WHERE

t.startterminal = 70

AND

t.duration IS NOT NULL

) r

GROUP BY hour

ORDER BY hour ASC;

</code></pre>

Since this data produces several numeric dimensions of data, we can visualize the results using a scatterplot graph, with the hour as the x-axis, number of trips as the y-axis, and the average duration as the scatterplot size.

[<img src="https://cdn.gethue.com/uploads/2015/08/hive_scatter-e1443111554498-1024x160.png" />][12]

Let's add another Hive snippet to analyze an hour-by-hour breakdown of availability at the SF Caltrain Station:

<pre><code class="sql">

SELECT

hour,

ROUND(AVG(bikes_available)) AS avg_bikes,

ROUND(AVG(docks_available)) AS avg_docks

FROM (

SELECT

r.time AS time,

CAST(SUBSTR(r.time, 12, 2) AS INT) AS hour,

CAST(r.bikes_available AS INT) AS bikes_available,

CAST(r.docks_available AS INT) AS docks_available

FROM \`bikeshare\`.\`rebalancing\` r

JOIN \`bikeshare\`.\`stations\` s ON r.station_id = s.station_id

WHERE

r.station_id = 70

AND

SUBSTR(r.time, 15, 2) = '00'

) t

GROUP BY hour

ORDER BY hour ASC;

</code></pre>

We'll visualize the results as a line graph, which indicates that the bike availability tends to fall starting at 6 AM and is regained around 6 PM.

[<img src="https://cdn.gethue.com/uploads/2015/08/hive_avg-e1443111570938-1024x169.png" />][13]

### Robust Data Analysis with PySpark

At a certain point, your data analysis may exceed the limits of relational analysis with SQL or require a more expressive, full-fledged API.

Hue's Spark notebooks allow users to mix exploratory SQL-analysis with custom Scala, Python (pyspark), and R code that utilizes the Spark API.

For example, we can open a pyspark snippet and load the trip data directly from the Hive warehouse and apply a sequence of filter, map, and reduceByKey operations to determine the average number of trips starting from the SF Caltrain Station:

<pre><code class="python">

trips = sc.textFile('/user/hive/warehouse/bikeshare.db/trips/201402_trip_data.csv')

trips = trips.map(lambda line: line.split(","))

station_70 = trips.filter(lambda x: x[4] == '70')

\# Emit tuple of ((date, hour), 1)

trips_by_day_hour = station_70.map(lambda x: ((x[2].split()[0], x[2].split()[1].split(':')[0]), 1))

trips_by_day_hour = trips_by_day_hour.reduceByKey(lambda a, b: a+b)

\# Emit tuple of (hour, count)

trips_by_hour = trips_by_day_hour.map(lambda x: (int(x[0][1]), x[1]))

avg_trips_by_hour = trips_by_hour.combineByKey( (lambda x: (x, 1)),

(lambda x, y: (x[0] + y, x[1] + 1)),

(lambda x, y: (x[0] + y[0], x[1] + y[1]))

)

avg_trips_by_hour = avg_trips_by_hour.mapValues(lambda v : v[0] / v[1])

avg_trips_sorted = sorted(avg_trips_by_hour.collect())

%table avg_trips_sorted

</code></pre>

[<img src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-23-23.13.46-e1443110910319-1024x268.png" />][14]

&nbsp;

As you can see, Hue's Notebook app enables easy interactive data analysis and visualizations with a powerful mix of tools. Want to know more about the Spark Notebook work, read about the [Livy, the Spark REST Job server][2] and see you at the upcoming [Spark Summit][15] in Amsterdam! The version is currently in beta and v1 is currently targeted for Hue 3.10 / CDH 5.7.

Stay tuned for a number of exciting improvements to the notebook app, and as usual feel free to comment on the [hue-user][16] list or [@gethue][17]!

&nbsp;

---

#### Helpful Tips

##### Importing quoted-CSV data

The BABS rebalancing data (named 201402_status_data.csv) uses quotes.  In these cases, it is easier to create the table in Hive in the Hive editor and use the OpenCSV Row SERDE for Hive:

<pre><code class="sql">

CREATE TABLE rebalancing(station_id int, bikes_available int, docks_available int, time string)

ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'

WITH SERDEPROPERTIES (

"separatorChar" = ",",

"quoteChar" = """,

"escapeChar" = "\"

)

STORED AS TEXTFILE;

</code></pre>

Then you can go back to the Metastore to import the CSV into the table; note that you may have to remove the header line manually.

##### Reset Impala's Metastore Cache

When you create new databases or tables and plan to query them in an Impala snippet, it's a good idea to run an INVALIDATE METADATA; command first to reset the metastore cache. Otherwise, you may encounter an error where the database or table is not recognized.

[1]: http://vision.cloudera.com/one-platform/
[2]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/
[3]: https://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/
[4]: https://gethue.com/spark-notebook-and-livy-rest-job-server-improvements/
[5]: https://gethue.com/hadoop-tutorial-create-hive-tables-with-headers-and/
[6]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.00.png
[7]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.54.png
[8]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.47.22.png
[9]: https://cdn.gethue.com/uploads/2015/09/impala_query.png
[10]: https://cdn.gethue.com/uploads/2015/08/impala_bar_graph.png
[11]: https://cdn.gethue.com/uploads/2015/08/impala_map.png
[12]: https://cdn.gethue.com/uploads/2015/08/hive_scatter.png
[13]: https://cdn.gethue.com/uploads/2015/08/hive_avg.png
[14]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-23-23.13.46.png
[15]: https://spark-summit.org/eu-2015/events/building-a-rest-job-server-for-interactive-spark-as-a-service/
[16]: http://groups.google.com/a/cloudera.org/group/hue-user
[17]: https://twitter.com/gethue
