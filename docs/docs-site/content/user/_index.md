+++
title = "User"
date = 2019-03-13T18:27:26-07:00
weight = 3
chapter = false
pre = "<b>2. </b>"
+++

This section describes the main functionalities from an end user point of view.

Hue consists in a single page interface that allow the users to perform data
analysis without losing any context. The goal is to promote self service and stay simple like Excel
so that 80% of the users can find, explore and query data and become more data driven.

Please refer to [connector section](/administrator/configuration/connectors/#databases) for the list of the most popular Database/Data Warehouse supported.

**1. Find or import your data**

Use the left metadata assists to browse your existing data without losing your editor. The top search will look through your saved queries and matching tables, columns and databases of connected [Data Catalogs](/user/browsing/#data-catalog). Objects can be tagged for a quick retrieval or assigning a more “humane” name. If the data does not exist yet, just drag & drop it to trigger the Create Table wizard and import it in just two steps.

**2. Query your data**

When you found your data, the [Editor's](/user/querying/#editor) autocomplete is extremely powerful and will highlight any syntax or logical error and provide risk alerts as well as inline documentation. The right assistant provides quick previews of the datasets, which columns or JOINs are popular and recommendations on how to type optimized queries. After the querying, refine your results before exporting to S3/HDFS/ADLS or downloaded as CSV/Excel.

**3. Applications**

* Editor: The goal of Hue's Editor is to make data querying easy and productive. It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, search & tagging of data and query assistance.
* Browsers: Hue's Browsers let you easily search, glance and perform actions on data or jobs in Cloud or on premise clusters.
* Dashboard: Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.
* Scheduler: The application lets you build workflows and then schedule them to run regularly automatically. A monitoring interface shows the progress, logs and allow actions like pausing or stopping jobs.


Each app of Hue can be extended to support your own languages or apps as detailed in the [developer guide](/developer/).
