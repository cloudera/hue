---
title: Brand new autocompleter for Hive and Impala
author: admin
type: post
date: 2016-08-26T08:58:54+00:00
url: /brand-new-autocompleter-for-hive-and-impala/
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:

---
Greetings SQL experts!

To make your [SQL editing][1] experience better we've created a brand new autocompleter for [Hue 3.11][2]. The old one had some limitations and was only aware of parts of the statement being edited. The new autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

The result is improved completion throughout. We now have completion for more than just `SELECT` statements, it will help you with the other DDL and DML statements too, `INSERT`, `CREATE`, `ALTER`, `DROP` etc.

#### Smart column suggestions

If multiple tables appear in the `FROM` clause, including derived and joined tables, it will merge the columns from all the tables and add the proper prefixes where needed. It also knows about your aliases, lateral views and complex types and will include those. It will now automatically backtick any reserved words or exotic column names where needed to prevent any mistakes.

<img width="896" height="378" data-gifffer="https://cdn.gethue.com/uploads/2016/08/autocomp_columns.gif"  />

<h4 style="margin-top: 100px;">
  Smart keyword completion
</h4>

The new autocompleter suggests keywords based on where the cursor is positioned in the statement. Where possible it will even suggest more than one word at at time, like in the case of `IF NOT EXISTS`, no one likes to type too much right? In the parts where order matters but the keywords are optional, for instance after `FROM tbl`, it will list the keyword suggestions in the order they are expected with the first expected one on top. So after `FROM tbl` the `WHERE` keyword is listed above `GROUP BY` etc.

<img width="654" height="200" data-gifffer="https://cdn.gethue.com/uploads/2016/08/autocomp_keywords.gif"  />

<h4 style="margin-top: 100px;">
  UDFs, what are the arguments for find_in_set?
</h4>

The improved autocompleter will now suggest functions, for each function suggestion an additional panel is added in the autocomplete dropdown showing the documentation and the signature of the function. The autocompleter know about the expected types for the arguments and will only suggest the columns or functions that match the argument at the cursor position in the argument list.

<img width="1050" height="188" data-gifffer="https://cdn.gethue.com/uploads/2016/08/autocomp_udf.gif"  />

<h4 style="margin-top: 100px;">
  Sub-queries, correlated or not
</h4>

When editing subqueries it will only make suggestions within the scope of the subquery. For correlated subqueries the outside tables are also taken into account.

<img width="728" height="152" data-gifffer="https://cdn.gethue.com/uploads/2016/08/autocomp_subquery_types.gif"  />

<h4 style="margin-top: 100px;">
  All about quality!
</h4>

We've fine-tuned the live autocompletion for a better experience and we've introduced some options under the editor settings where you can turn off live autocompletion or disable the autocompleter altogether (if you're adventurous). To access these settings open the editor and focus on the code area, press `CTRL + ,` (or on Mac `CMD + ,`) and the settings will appear.

The autocompleter talks to the backend to get data for tables and databases etc. by default it will timeout after 5 seconds but once it has been fetched it's cached for the next time around. The timeout can be adjusted in the Hue server configuration.

We've got an extensive test suite but not every possible statement is covered, if the autocompleter can't interpret a statement it will be silent and no drop-down will appear. If you encounter a case where you think it should suggest something but doesn't or if it gives incorrect suggestions then please let us know.

&nbsp;

As usual you can send feedback and participate on the [hue-user][3] list or [@gethue][4]!

&nbsp;

 [1]: https://gethue.com/sql-editor-for-solr-sql/
 [2]: https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
