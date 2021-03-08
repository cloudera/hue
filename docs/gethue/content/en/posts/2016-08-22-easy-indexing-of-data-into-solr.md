---
title: Easy indexing of data into Solr with ETL operations
author: admin
type: post
date: 2016-08-22T10:02:08+00:00
url: /easy-indexing-of-data-into-solr/
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
categories:
  - Tutorial
---

# **Creating Solr Collections from Data files in a few clicks**

<span style="font-weight: 400;">There are exciting new features coming in <a href="https://github.com/cloudera/hue/blob/master/docs/release-notes/release-notes-3.11.0.txt">Hue 3.11</a> week and later in CDH 5.9 this Fall. One of which is Hue’s brand new tool to create <a href="http://lucene.apache.org/solr/">Apache Solr</a> Collections from file data. <a href="https://gethue.com/dynamic-search-dashboard-improvements-3/">Hue’s Solr dashboards</a> are great for visualizing and learning more about your data so being able to easily load data into Solr collections can be really useful. </span>

<span style="font-weight: 400;">In the past, indexing data into Solr has been quite difficult. </span>[<span style="font-weight: 400;">The task</span>][1] <span style="font-weight: 400;">involved writing a Solr schema and a morphlines file then submitting a job to YARN to do the indexing. Often times getting this correct for non trivial imports could take a few days of work. Now with Hue’s new feature you can start your YARN indexing job in minutes. This tutorial offers a step by step guide on how to do it.</span>

&nbsp;

{{< youtube uS0MpzW0ep8 >}}

&nbsp;

# Tutorial

## **What you’ll need**

<span style="font-weight: 400;">First you'll need to have a running Solr cluster that Hue is configured with.</span>

<span style="font-weight: 400;">Next you'll need to install these required <a href="https://www.dropbox.com/s/unex80g7xbx1aq7/smart_indexer_lib-2016-08-22.zip?dl=0">libraries</a>. To do so place them in a directory somewhere on HDFS and set the path for </span>_<span style="font-weight: 400;">config_indexer_libs_path</span>_ <span style="font-weight: 400;">under indexer in the Hue ini to match by default, the </span>_<span style="font-weight: 400;">config_indexer_libs_path</span>_ <span style="font-weight: 400;">value is set to </span>_<span style="font-weight: 400;">/tmp/smart_indexer_lib</span>_<span style="font-weight: 400;">. Additionally under indexer in the Hue ini you’ll need to set </span>_<span style="font-weight: 400;">enable_new_indexer </span>_<span style="font-weight: 400;">to true</span><span style="font-weight: 400;">.</span>

<pre><code class="bash">

[indexer]

\# Flag to turn on the morphline based Solr indexer.

enable_new_indexer=false

\# Oozie workspace template for indexing.

\## config_indexer_libs_path=/tmp/smart_indexer_lib

</code></pre>

**Note**:

If using Cloudera Manager, check how to [add properties in Hue.ini safety valve][2] and put the abov

## Selecting data

<span style="font-weight: 400;">We are going to create a new Solr collection from <a href="https://cdn.gethue.com/downloads/reviews_data.csv">business review data</a>. To start let’s put the data file somewhere on HDFS so we can access it.</span>

[<img class="aligncenter wp-image-4305" src="https://cdn.gethue.com/uploads/2016/08/data-file-indexer-1024x503.png" />][3]

&nbsp;

<span style="font-weight: 400;">Now we can get started! Under the search tab in the navbar select Index.</span>

[<img class="aligncenter wp-image-4307" src="https://cdn.gethue.com/uploads/2016/08/indxer-menu.png" />][4]

&nbsp;

<span style="font-weight: 400;">We'll pick a name for our new collection and select our reviews data file from HDFS. Then we'll click next.</span>

[<img class="aligncenter wp-image-4309" src="https://cdn.gethue.com/uploads/2016/08/indexer-wizard-1024x524.png" />][5]

## Field selection and ETL

<span style="font-weight: 400;">On this tab we can see all the fields the indexer has picked up from the file. Note that Hue has also made an educated guess on the field type. Generally, Hue does a good job inferring data type. However, we should do a quick check to confirm that the field types look correct.</span>

[<img class="aligncenter wp-image-4311" src="https://cdn.gethue.com/uploads/2016/08/indexer-wizard-fields-1024x520.png" />][6]

&nbsp;

For our data we're going to perform 4 operations to make a very searchable Solr Collection.

1. Convert Date


    This operation is implicit. By setting the field type to date we inform Hue that we want to convert this date to a Solr Date. Hue can convert most standard date formats automatically. If we had a unique date format we would have to define it for Hue by explicitly using the convert date operation.

    [<img class="aligncenter wp-image-4312" src="https://cdn.gethue.com/uploads/2016/08/indexer-op-date-1024x63.png" />][7]

<ol start="2">
  <li>
    Translate star ratings to integer ratings<br /> Under the rating field we’ll change the field type from string to long and click add operation. We’ll then select the translate operation and setup the following translation mapping.<br /> <a href="https://cdn.gethue.com/uploads/2016/08/indexer-translate-date.png"><img class="aligncenter wp-image-4313" src="https://cdn.gethue.com/uploads/2016/08/indexer-translate-date-1024x373.png" /></a>
  </li>
</ol>

<ol start="3">
  <li>
    Grok the city from the full address field<br /> We’ll add a grok operation to the full address field, fill in the following regex <i>.* (?<city>\w+),.* </i>and set the number of expected fields to 1. In the new child field we’ll set the name to city. This new field will now contain the value matching the city capture group in the regex.<br /> <a href="https://cdn.gethue.com/uploads/2016/08/indexer-op-grok.png"><img class="aligncenter wp-image-4314" src="https://cdn.gethue.com/uploads/2016/08/indexer-op-grok-1024x188.png" /></a>
  </li>
</ol>

<ol start="4">
  <li>
    Use a split operation to separate the latitude/longitude field into two separate floating point fields.<br /> Here we have an annoyance. Our data file contains the latitude and longitude of the place that’s being reviewed - Awesome! For some reason though they’ve been clumped into one field with a comma between the two numbers. We’ll use a split operation to grab each individually. Set the split value to ‘,’ and the number of output fields to 2. Then change the child fields’ types to doubles and give them logical names. In this case there’s not really much sense in keeping the parent field so let’s uncheck the “keep in index” box.<br /> <a href="https://cdn.gethue.com/uploads/2016/08/indexer-op-split.png"><img class="aligncenter wp-image-4316" src="https://cdn.gethue.com/uploads/2016/08/indexer-op-split-1024x231.png" /></a>
  </li>
</ol>

<ol start="5">
  <li>
    perform a GeoIP to find where the user was when they submitted the review<br /> Here we’ll add a geo ip operation and select iso_code as our output. This will give us the country code.<br /> <a href="https://cdn.gethue.com/uploads/2016/08/indexer-op-geoip.png"><img class="aligncenter wp-image-4317" src="https://cdn.gethue.com/uploads/2016/08/indexer-op-geoip-1024x165.png" /></a>
  </li>
</ol>

&nbsp;

## **Indexing**

Before we index, let’s make sure everything looks good with a quick scan of the preview. This can be handy to avoid any silly typos or anything like that.

Now that we've defined our ETL Hue can do the rest. Click index and wait for Hue to index our data. At the bottom of this screen we can see a progress bar of the process. Yellow means our data is currently being indexed and green means it's done. Feel free to close this window. The indexing will continue on your cluster.

Once our data has been indexed into a Solr Collection we have access to all of Hue's search features and can make a nice analytics dashboard like this one for our data.

[<img src="https://cdn.gethue.com/uploads/2016/08/indexer-dash-1024x486.png" />][8]

&nbsp;

# Documentation

## **Assembling the lib directory yourself**

The indexer libs path is where all required libraries for indexing should be. If you’d prefer you can assemble this directory yourself. There are three main components to the libs directory:

1. JAR files required by the [MapReduceIndexerTool][9]

- All required jar files should have shipped with CDH. Currently the list of required JARs is:
  - argparse4j-0.4.3.jar
  - readme.txt
  - httpmime-4.2.5.jar
  - search-mr-1.0.0-cdh5.8.0-job.jar
  - kite-morphlines-core-1.0.0-cdh5.8.0.jar
  - solr-core-4.10.3-cdh5.8.0.jar
  - kite-morphlines-solr-core-1.0.0-cdh5.8.0.jar
  - solr-solrj-4.10.3-cdh5.8.0.jar
  - noggit-0.5.jar
- Should this change and you get a missing class error, you can find whatever jar may be missing by grepping all the jars packaged with CDH for the missing class.

2. Maxmind GeoLite2 database

- This file is required for the GeoIP lookup command and can be found on [MaxMind’s website][10]

3. Grok Dictionaries

- Any grok commands can be defined in text files within the grok_dictionaries sub directory. A good starter set of grok dictionaries can be found [here][11].

&nbsp;

## **Operations**

<span style="font-weight: 400;">On top of the ease of use, this is where the real power of Hue's new indexer lies. Heavily leveraging <a href="http://kitesdk.org/docs/0.17.1/morphlines/morphlines-reference-guide.html">Morphlines</a>, operations let us easily transform our data into a more searchable format. Before we add some to our fields let's quickly go over the operations that the indexer offers.</span>

<span style="font-weight: 400;">Operation list:</span>

<li style="font-weight: 400;">
  <strong>Split</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">With the split operation we can take a field and produce new fields by splitting the original field on a delimiting character</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “2.1,-3.5,7.1”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Split Character: “,”</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Outputs 3 fields:</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Field 1: “2.1”<br /> </span>Field 2: “-3.5”<br /> Field 3: “7.1”
    </li>
  </ul>
</li>

<li style="font-weight: 400;">
  <strong>Grok</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Grok is an extension of Regex and can be used to match specific subsections of a field and pull them out. You can read more about the Grok syntax </span><a href="https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html"><span style="font-weight: 400;">here</span></a>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “Winnipeg (Canada)”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Regular Expression: “\w+ \((?<country>\w+)\)”</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Outputs 1 field:</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;"><span style="font-weight: 400;">country: “Canada”</span></span>
    </li>
  </ul>
</li>

<li style="font-weight: 400;">
  <strong>Convert Date</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Generally the indexer converts dates automatically to Solr's native format. However, if you have a very obscure date format you can define it using a </span><a href="http://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html"><span style="font-weight: 400;">SimpleDateFormat</span></a><span style="font-weight: 400;"> here to ensure it is converted correctly</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “Aug (2016) 24”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Date Format: “MMM (YYYY) dd”</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Output: </span><span style="font-weight: 400;"><span style="font-weight: 400;">In place replacement: “2016-08-24T00:00:00Z”</span></span>
    </li>
  </ul>
</li>

<li style="font-weight: 400;">
  <strong>Extract URI Components</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Extract URI Components lets you grab specific parts of a URI and put it in its own field without having to write the Regex yourself.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">The following components can be extracted:</span> <ul>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Authority</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Fragment</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Host</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Path</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Port</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Query</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Scheme</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Scheme Specific Path</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">User Info</span>
        </li>
      </ul>
    </li>

    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “</span><a href="https://www.google.com/#q=cloudera+hue"><span style="font-weight: 400;">https://www.google.com/#q=cloudera+hue</span></a><span style="font-weight: 400;">”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Selected: Host</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;"><span style="font-weight: 400;">Output: “www.google.com”</span></span>
    </li>

  </ul>
</li>

<li style="font-weight: 400;">
  <strong>Geo IP</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Geo IP performs a Maxmind GeoIP lookup to match public IP addresses with a location.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">The following location information can be extracted with this operation:</span> <ul>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">ISO Code</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Country Name</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Subdivision Names</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Subdivision ISO Code</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">City Name</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Postal Code</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Latitude</span>
        </li>
        <li style="font-weight: 400;">
          <span style="font-weight: 400;">Longitude</span>
        </li>
      </ul>
    </li>

    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “74.217.76.101”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Selected: ISO Code, City Name, Latitude, Longitude</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;"><span style="font-weight: 400;">Output: “US”,  “Palo Alto”, “37.3762”, “-122.1826”</span></span>
    </li>

  </ul>
</li>

<li style="font-weight: 400;">
  <strong>Translate</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Translate will take given hard coded values and replace them with set values in place.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “Five Stars”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Mapping:</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">“Five Stars” -> “5”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">“Four Stars” -> “4”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">“Three Stars” -> “3”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">“Two Stars” -> “2”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">“One Star” -> “1”</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Output: </span><span style="font-weight: 400;"><span style="font-weight: 400;">In place Replacement: “5”</span></span>
    </li>
  </ul>
</li>

<li style="font-weight: 400;">
  <strong>Find and Replace</strong> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Find and Replace takes a Grok string as the find argument and will replace all matches in the field with the specified replace value in place.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Input: “Hello World”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Find: “(?<word>\b\w+\b)”</span><span style="font-weight: 400;"><br /> </span><span style="font-weight: 400;">Replace: “"${word}!"</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">Output: </span><span style="font-weight: 400;">In place replacement: “Hello! World!”</span>
    </li>
  </ul>
</li>

&nbsp;

## **Supported Input Data**

Hue successfully recognized our file as a CSV. The indexer currently supports the following file types:

- CSV Files
- Hue Log Files
- Combined Apache Log Files
- Ruby Log File
- Syslog

Beyond files, metastore tables and Hive SQL queries are also supported. Read more about these in an upcoming 3.11 blog post.

&nbsp;

## **Troubleshooting\*\***

\*\*

<span style="font-weight: 400;">During the indexing process records can be dropped if they fail to match the Solr Schema. (e.g., trying to place a string into a long field). If some of your records are missing and you are unsure why you can always check the mapper log for the indexing job to get a better idea on what’s going on.</span>\*\*\*\*

&nbsp;

[1]: https://gethue.com/hadoop-tutorials-season-ii-7-how-to-index-and-search/
[2]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
[3]: https://cdn.gethue.com/uploads/2016/08/data-file-indexer.png
[4]: https://cdn.gethue.com/uploads/2016/08/indxer-menu.png
[5]: https://cdn.gethue.com/uploads/2016/08/indexer-wizard.png
[6]: https://cdn.gethue.com/uploads/2016/08/indexer-wizard-fields.png
[7]: https://cdn.gethue.com/uploads/2016/08/indexer-op-date.png
[8]: https://cdn.gethue.com/uploads/2016/08/indexer-dash.png
[9]: http://www.cloudera.com/documentation/enterprise/5-5-x/topics/search_mapreduceindexertool.html
[10]: https://dev.maxmind.com/geoip/geoip2/geolite2/
[11]: https://github.com/kite-sdk/kite/tree/master/kite-morphlines/kite-morphlines-core/src/test/resources/grok-dictionaries
