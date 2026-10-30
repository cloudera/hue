---
title: "Concepts"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

## Interface

Hue is a single-page app with a simple layout.

![image](/images/hue-4-interface-concept.png)

From top to bottom we have:

* Quick action (big blue button), a global search and a notification area on the right
* A collapsible hamburger menu that offers links to the various apps and a quick way to import data
* An extended quick browse on the left
* The main app area, where you work
* A right Assistant panel for the current application. Its content depends on the selected application. For example, in the Editor it shows the tables used in your query, the SQL language reference, and built-in function (UDF) documentation.

Learn more in [The Hue 4 user interface in detail](http://gethue.com/the-hue-4-user-interface-in-detail/).


### Top search

Use the search bar at the top of the screen to find any table, view, or column across all databases. It also searches your saved documents. Metadata search is available when your administrator has configured a metadata server.

![Top Search](https://cdn.gethue.com/uploads/2016/04/table_search.png)


### Left assist

Data where you need it when you need it.

Use the left assist panel to find your documents, databases, tables, and files. Right-click an item to see its actions. Drag and drop a file to insert its path into the editor.

![Left assist Navigation and drop](https://cdn.gethue.com/uploads/2018/05/HDFS_Context_Change_Path_2.gif)

### Right assist

The content of this panel depends on the selected application. In the Editor, it shows the tables used in the query, the language reference, and the available functions (UDFs).

### Sample popup

This popup offers a quick way to see sample of the data and other statistics on databases, tables, and columns. Open the popup from the left assist panel or right-click any SQL object (table, column, function) in the editor.

![Sample popup Navigation](https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif)

## Documents

Like in Google Docs, you can share any document (for example a SQL query or a dashboard) with other users or groups.

### Sharing

Share a document from the Documents page or from the top-right menu of the application.

Two types of sharing permissions exist:

- Read only
- Can modify

Shared documents will show-up with a little blue icon.

![Sharing](https://cdn.gethue.com/uploads/2019/04/editor_sharing.png)

Two faster options are also available: public links and gist sharing.

#### Public Links

Public links work like links in Google Docs. Use them to quickly share saved, parameterized reports. The recipient only needs a Hue login. Recipients can run the query to see the results, then fork and adapt it.

- No need to select groups or list of individual users
- Read or write permissions
- Linked documents won't show up in your home
- Can be turned off globally by your administrator (`enable_link_sharing`)
- Can be combined with traditional user/group sharing

The sharing dialog shows the public link option at the top when it is enabled:

![Public Link](https://cdn.gethue.com/uploads/2020/03/editor_sharing_popup.png)

#### Gist Sharing - SQL Snippet

Use a gist to quickly share a SQL snippet, for example in a Slack channel. The gist is a direct link to the Editor.

- Works with an SQL snippet: one or more statements
- The link points to the Editor with the SQL content
- The query is displayed in the [presentation mode](/user/querying/#presentation)
- Slack shows a mini preview of the link (your administrator can turn this off with `enable_gist_preview`)
- Gists are stored in a `Gist` directory in your home directory

To share a gist:

1. Select the statements to share.
2. Open the editor **More** menu and select **Shareable link**.

![Get Sharable Link](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_menu.png)

Hue generates the link to the SQL fragment:

![Gist](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_popup.png)

Paste the link in a Slack channel to show a mini preview:

![Gist in Slack](https://cdn.gethue.com/uploads/2020/03/editor_gist_slack.png)

Clicking the link opens the SQL selection:

![Click Gist](https://cdn.gethue.com/uploads/2020/03/editor_gist_open_presentation_mode.png)

### Import / Export

Use the Documents page to export saved documents for backup or to transfer them to another Hue.

## Slack

**Note**: The Slack integration is in beta.

This integration helps you share and discuss SQL queries with other users in Slack.

To set up the Hue app, your Slack workspace administrator must follow the [installation steps](/administrator/configuration/server/#easier-slack-app-installation).

After the app is connected to Hue, type `hello hue` or `@Hue help` in the Slack channel to list what the app can do.

![SQL Assistant Help GIF](https://cdn.gethue.com/uploads/2021/06/hello_hue.gif)

### Sharing Query/Gist links
You can share query links or gists in Slack channels where the Hue app is present. Slack shows a rich preview of the query. If results are available, the app also posts the result file in the message thread.

Open the Editor, run a query, and copy its link:

![Run Query in Hue](https://cdn.gethue.com/uploads/2021/04/run_query_in_hue.png)

Paste the link in the Slack channel to show a rich preview:

![Query Link Preview](https://cdn.gethue.com/uploads/2021/04/query_link_preview.png)

Slack does not support Markdown tables. The preview therefore shows a few sample rows with all columns, pivoted. The app posts the full result file in the message thread.

![Message Thread with Result File](https://cdn.gethue.com/uploads/2021/04/message_thread_with_result_file.png)

You can also share SQL gist links:

![Gist Link](https://cdn.gethue.com/uploads/2021/04/gist_link.png)

![Gist Link Preview](https://cdn.gethue.com/uploads/2021/04/gist_link_preview.png)

### Directly Share from Editor
You can share a query from the Editor directly to a Slack channel. The app posts the gist link in the selected channel, and Slack shows a rich preview. Your administrator can turn this off with `share_from_editor`.

Create a gist, select a channel, and share it from the Editor:

![Share from Editor GIF](https://cdn.gethue.com/uploads/2021/06/share_from_editor.gif)

### Assistance

#### Detecting SQL SELECT statements
When a message contains a SELECT statement, the Hue app suggests sharing a link instead of pasted SQL. It also posts a gist link for the detected SQL, which Slack shows as a rich preview.

![Detect SQL GIF](https://cdn.gethue.com/uploads/2021/06/detect_sql_select.gif)

#### Query Bank
Type `@Hue queries` in the channel to list important and frequently used queries from the latest query bank.

![Query Bank GIF](https://cdn.gethue.com/uploads/2021/06/hue_query_bank.gif)

### Security
Slack users must also be Hue users to use these features. Hue maps a Slack user to a Hue user when the **email prefix matches the Hue username** and the **email host matches the domain of the Hue instance** connected to the app.

For example, the Slack user `alice@gethue.com` can only access the Hue user `alice` on `demo.gethue.com`.

## Settings

### Landing page

Star an application or editor next to its name to make it the default editor and the landing page when you log in.

### Changing the language

Hue detects the language from your browser or operating system. English, Spanish, French, German, Korean, Japanese, Portuguese, Brazilian Portuguese, and Simplified Chinese are supported.

To set the language manually:

1. Open **My Profile**.
2. Go to **Step 2: Profile and Groups** (**Step 2: Profile** for non-admin users).
3. Select a **Language Preference**.
4. Save your changes.
