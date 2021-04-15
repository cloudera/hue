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

This popup offers a quick way to see sample of the data and other statistics on databases, tables, and columns. You can open the popup from the SQL Assist or with a right-click on any SQL object (table, column, function…).

![Sample popup Navigation](https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif)

## Documents

Similarly to Google Documents, any document (e.g. SQL Query, Workflow, Dashboard...) opened in the Hue apps can be shared with other users or groups.

### Sharing

Sharing happens on the main page or via the top right menu of the selected application.

Two types of sharing permissions exist:

- Read only
- Can modify

Shared documents will show-up with a little blue icon.

![Sharing](https://cdn.gethue.com/uploads/2019/04/editor_sharing.png)

Along with document sharing, there is another query sharing option via links which is quicker and easier - **Public Links & Gist Sharing**

#### Public Links

Public links are the same as in Google documents which helps in quickly sharing parameterized saved reports, customer analyses links. They only require the recipient to have a Hue login. People can then reuse the queries on their own by executing them to see the results, fork and adapt them.

- No need to select groups or list of individual users
- Read, write permissions
- Linked documents won't show up in your home
- Can be turned off globally
- Can be combined with traditional user/group sharing

Here is the sharing popup with the public link option on the top when globally enabled:

![Public Link](https://cdn.gethue.com/uploads/2020/03/editor_sharing_popup.png)

#### Gist Sharing - SQL Snippet

Answering a question via a query result? Showing some weird data to a slack channel? Gist are a great quick way to quickly share SQL snippets, with a direct link to the SQL editor.

- Works with an SQL snippet: one or more statements
- The link automatically point to the editor and the SQL content
- The query is displayed in the friendlier [presentation mode](/user/querying/#presentation)
- Slack unfurling will show a mini preview (can be turned off globally)
- Gists are stored in a Gist directory in your home

Here is an example:

Select a portion of statements to quick share with a Slack channel:

![Get Sharable Link](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_menu.png)

The link to the SQL fragment is automatically generated:

![Gist](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_popup.png)

Just paste the link in the Slack channel and users will get a mini preview:

![Gist in Slack](https://cdn.gethue.com/uploads/2020/03/editor_gist_slack.png)

Clicking on the link will open-up the SQL selection:

![Click Gist](https://cdn.gethue.com/uploads/2020/03/editor_gist_open_presentation_mode.png)

### Import / Export

Via the Home page, saved documents can be exported for backups or transferring to another Hue.

## Slack
Currently in **Beta**

This integration increases the collaboration with other users via Slack.

### Share to Slack
This feature expands the ability to share query links or gists to the desired Slack channels which then unfurls in a rich preview for other users. It even gives the user result file for the query if it has not expired.

To manually set-up the Hue App, follow the steps mentioned in the [bot setup](/administrator/configuration/server/#manual-slack-app-installation) described in the Admin section.

Open Hue, run some query and copy its link:

![Run Query in Hue](https://cdn.gethue.com/uploads/2021/04/run_query_in_hue.png)

Paste it in the Slack channel for others to get a rich link preview:

![Query Link Preview](https://cdn.gethue.com/uploads/2021/04/query_link_preview.png)

Slack currently does not support markdown tables and potential improvements with inline preview will come when Hue supports result caching via [query tasks](/administrator/administration/reference/#task-server)

After evaluating a lot of possible fixes ( like uploading result image, truncating columns which doesn't look good, pivoting table, uploading result file etc.) and seeing their tradeoffs, we chose to have few sample rows but keep all columns by pivoting the result table and to compensate for the loss of rows, Hue app gives the result file in the message thread.

![Message Thread with Result File](https://cdn.gethue.com/uploads/2021/04/message_thread_with_result_file.png)

Users can share the SQL gists too!

![Gist Link](https://cdn.gethue.com/uploads/2021/04/gist_link.png)

![Gist Link Preview](https://cdn.gethue.com/uploads/2021/04/gist_link_preview.png)

#### Security
Keeping in mind the security aspect, those Slack users who are Hue users and have the read permissions to access the query and its result will get this rich preview and result file after sharing the link. This mapping is currently done by checking the email prefix and its host for Hue username.

For example, some person ‘Alice’ having a Hue account with username ‘alice’ can have read access from some Slack account only if the email prefix of that slack user is same and Hue username and the email host is same in the Hue domain i.e. **alice@gethue.com slack user** can only access **Hue user ‘alice’** on **‘demo.gethue.com’** 

## Settings

### Landing page

Any application or editor can be starred next to its name so that it becomes the default editor and the landing page when logging in.

### Changing the language

The language is automatically detected from the Browser or OS. English, Spanish, French, German, Korean, Japanese and Chinese are supported.

The language can be manual set by a user in the "My Profile" page. Please go to My Profile > Step2 Profile and Groups > Language Preference and choose the language you want.
