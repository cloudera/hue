---
title: "Concepts"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

## Interface

The layout simplifies the interface and is a snappy single page app.

![image](/images/hue-4-interface-concept.png)

From top to bottom we have:

* Quick action (big blue button), a global search and a notification area on the right
* A collapsible hamburger menu that offers links to the various apps and a quick way to import data
* An extended quick browse on the left
* The main app area, where the fun is ;)
* A right Assistant panel for the current application. It offers a live help and depends on the currently selected application. For example in the Hive Editor, it shows a quick browse for the used tables in your query, suggestions on how to write better queries, SQL language and UDF built-in documentation.

Learn more on the [The Hue 4 user interface in detail](http://gethue.com/the-hue-4-user-interface-in-detail/).


### Top search

Have you ever struggled to remember table names related to your project? Does it take much too long to find those columns or views? Hue now lets you easily search for any table, view, or column across all databases in the cluster. With the ability to search across tens of thousands of tables, you're able to quickly find the tables that are relevant for your needs for faster data discovery.

The new search bar is always accessible on the top of screen, and it offers a document search and metadata search too if Hue is configured to access a metadata server.

![Top Search](https://cdn.gethue.com/uploads/2016/04/table_search.png)


### Left assist

Data where you need it when you need it.

Find your documents, HDFS and S3 files and more in the left assist panel, right-clicking items will show a list of actions, you can also drag-and-drop a file to get the path in your editor and more.

![Left assist Navigation and drop](https://cdn.gethue.com/uploads/2018/05/HDFS_Context_Change_Path_2.gif)

### Right assist

This assistant content depends on the context of the application selected and will display the current tables or available UDFs.

### Sample popup

This popup offers a quick way to see sample of the data and other statistics on databases, tables, and columns. You can open the popup from the SQL Assist or with a right-click on any SQL object (table, column, function…). In this release, it also opens faster and caches the data.

![Sample popup Navigation](https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif)

## Documents

Similarly to Google Documents, any document (e.g. SQL Query, Workflow, Dashboard...) opened in the Hue apps can be saved.

### Sharing

Sharing happens on the main page or via the top right menu of the selected application.

Two types of sharing permissions exist:

- Read only
- Can modify

Shared documents will show-up with a little blue icon.

![Sharing](https://cdn.gethue.com/uploads/2019/04/editor_sharing.png)

### Import / Export

Via the Home page, saved documents can be exported for backups or transferring to another Hue.

## Settings

### Landing page

Any application or editor can be starred next to its name so that it becomes the default editor and the landing page when logging in.

### Changing the language

The language is automatically detected from the Browser or OS. English, Spanish, French, German, Korean, Japanese and Chinese are supported.

The language can be manual set by a user in the "My Profile" page. Please go to My Profile > Step2 Profile and Groups > Language Preference and choose the language you want.
