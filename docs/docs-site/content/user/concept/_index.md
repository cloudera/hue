---
title: "Concepts"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

Hue consists in 4 apps in a single page interface that allow the users to perform data
analyses without losing any context. The goal is to promote self service and stay simple like Excel
so that 80% of the user can find, explore and query data and become more data driven.

**1. Find or import your data**

Use the left metadata assists to browse your existing data without losing your editor. The top search will look through your saved queries and matching tables, columns and databases. Objects can be tagged for a quick retrieval or assigning a more “humane” name. If the data does not exist yet, just drag & drop it to trigger the Create Table wizard and to import it in just two steps.

**2. Query your data**

When you found your data, the Editor's autocomplete is extremely powerful as they support 90-100% of the language syntax and will highlight any syntax or logical error. The right assistant provides quick previews of the datasets, which columns or JOINs are popular and recommendations on how to type optimized queries. After the querying, refine your results before exporting to S3/HDFS/ADLS or downloaded as CSV/Excel.

** 4 applications**

* Editor: The goal of Hue's Editor is to make data querying easy and productive. It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, search & tagging of data and query assistance.
* Browsers: Hue's Browsers let you easily search, glance and perform actions on data or jobs in Cloud or on premise clusters.
* Dashboard: Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.
* Scheduler: The application lets you build workflows and then schedule them to run regularly automatically. A monitoring interface shows the progress, logs and allow actions like pausing or stopping jobs.


Each app of Hue can be extended to support your own languages or apps as detailed in the [SDK](../sdk/sdk.html).

## Interface

The layout simplifies the interface and is now single page app, and this makes things snappier and unifies the apps together.

![image](/images/hue-4-interface-concept.png)

From top to bottom we have:

* A completely redesigned top bar, with a quick action (big blue button), a global search and a notification area on the right
* A collapsible hamburger menu that offers links to the various apps and a quick way to import data
* An extended quick browse on the left
* The main app area, where the fun is ;)
* A right Assistant panel for the current application. It's now enabled for the editors, and in case of Hive for instance, it offers you a live help, a quick browse for the used tables in your query, and much more: if your Hue instance is connected to a SQL Optimizer service like Cloudera Navigator Optimizer, it can offer suggestions on your queries!
* Various applications have been grouped into 4 main conceptual areas:

Learn more on the [The Hue 4 user interface in detail](http://gethue.com/the-hue-4-user-interface-in-detail/).


## Top search

The new search bar is always accessible on the top of screen, and it offers a document search and metadata search too if Hue is configured to access a metadata server like Cloudera Navigator.

### Embedded Search & Tagging

Have you ever struggled to remember table names related to your project? Does it take much too long to find those columns or views? Hue now lets you easily search for any table, view, or column across all databases in the cluster. With the ability to search across tens of thousands of tables, you're able to quickly find the tables that are relevant for your needs for faster data discovery.

In addition, you can also now tag objects with names to better categorize them and group them to different projects. These tags are searchable, expediting the exploration process through easier, more intuitive discovery.

Through an integration with Cloudera Navigator, existing tags and indexed objects show up automatically in Hue, any additional tags you add appear back in Cloudera Navigator, and the familiar Cloudera Navigator search syntax is supported.

A top search bar now appears. The autocomplete offers a list of facets and prefills the top values. Pressing enter lists the available objects, which can be opened and explored further in the sample popup, the assist or directly into the table browser app.

### Granular Search

By default, only tables and views are returned. To search for columns, partitions, databases use the ‘type:' filter.

Example of searches:

* table:customer → Find the customer table
* table:tax* tags:finance → List all the tables starting with tax and tagged with ‘finance'
* owner:admin type:field usage → List all the fields created by the admin user that matches the usage string
* parentPath:"/default/web_logs" type:FIELD  originalName:b* → List all the columns starting with `b` of the table `web_logs` in the database `default`.

Learn more on the [Search and Tagging](https://blog.cloudera.com/blog/2017/05/new-in-cloudera-enterprise-5-11-hue-data-search-and-tagging/).

## Left assist

Data where you need it when you need it

You can now find your Hue documents, HDFS and S3 files and more in the left assist panel, right-clicking items will show a list of actions, you can also drag-and-drop a file to get the path in your editor and more.

## Right assist
This assistant content depends on the context of the application selected and will display the current tables or available UDFs.

## Sample popup

This popup offers a quick way to see sample of the data and other statistics on databases, tables, and columns. You can open the popup from the SQL Assist or with a right-click on any SQL object (table, column, function…). In this release, it also opens faster and caches the data.

## Documents

Similarly to Google Document, queries, workflows... can be saved and shared with other users.

### Sharing

Sharing happens on the main page or via the top right menu of the application. Users and groups with Read or Write permissions can be selected.

### Import / Export

Via the Home page, saved documents can be exported for backups or transferring to another Hue.

## Changing the language

The language is automatically detected from the Browser or OS. English, Spanish, French, German, Korean, Japanese and Chinese are supported.

The language can be manual set by a user in the "My Profile" page. Please go to My Profile > Step2 Profile and Groups > Language Preference and choose the language you want.