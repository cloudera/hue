---
title: SQL Assist and Autocomplete Improvements
author: admin
type: post
date: 2015-11-05T11:59:54+00:00
url: /assist-and-autocomplete-improvements/
sf_remove_promo_bar:
  - 1
sf_caption_position:
  - caption-right
sf_right_sidebar:
  - Sidebar-1
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_social_sharing:
  - 1
sf_background_image_size:
  - cover
sf_page_title_text_style:
  - light
sf_page_title_bg:
  - none
sf_thumbnail_type:
  - none
sf_no_breadcrumbs:
  - 1
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
categories:
---

We've recently made some nice improvements to the autocomplete and assist panel that should really boost the experience when working with the [notebooks][1] or editing SQL queries in the Hive and Impala query [editors][2].

One of the major improvements is support for complex types; structs, maps and arrays, both in the assist and autocomplete. See more of the improvements below or take a look at the following video demo.

&nbsp;

{{< youtube PciZhDY-W5A >}}

A longer more detailed version is available [here][3].

&nbsp;

### Complex in a simple way...

The assist panel now support complex types for Hive and Impala. Just click on the column and it'll expand any of the structs, maps and arrays.

We've made the assist panel resizable, which is very handy when you have long table or column names or deep nested structures.

[<img src="https://cdn.gethue.com/uploads/2015/11/Assist_complex-1024x777.png"  />][4]

&nbsp;

If you find what you're looking for in the panel you can double-click the item to insert it at the cursor in the active editor. You can also drag-and-drop it anywhere in the editor if you prefer another location. It knows about the structure and will insert the reference with all the parents up to and including the column name.

&nbsp;

### Ctrl+space is your friend!

You can use ctrl+space anywhere in the editor to activate the autocomplete. It will make suggestion based on the schema and it will also take the contents of the statement that you're editing into account. Apart from the SQL keywords, tables and columns it will even suggest user-defined aliases.

[<img src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_join_alias-1024x387.png"  />][5]

&nbsp;

It knows about complex types for Hive and Impala and will make the appropriate suggestions based on the reference that you're currently editing.

[<img src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_nested_struct-1024x448.png"  />][6]

&nbsp;

I heard you like exploded views! The autocomplete will help you with these, it keeps track of the exploded views as well as exploded views of exploded views of exploded views of...

[<img src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_exploded-1024x300.png"  />][7]

&nbsp;

### Values and HDFS paths

We've even added sample values to the mix. It's currently only available for Impala and it will suggest a subset of all the values, this is really nice when working with for instance map keys or to give you an idea of the data.

[<img src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_sample_values.png"  />][8]

&nbsp;

Last but not least, the autocomplete can now suggest HDFS paths. Just type '/' in one of the notebook snippets and it will automatically open the autocomplete panel with the list of folders and files at that location, of course you can also activate it with ctrl+space when editing an existing path.

[<img src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_hdfs-1024x337.png"  />][9]

&nbsp;

We'll keep improving the assist and autocomplete experience (support for HBase, any JDBC database, HDFS...) and hope that these new features will be useful for you!

Feel free to send feedback on the [hue-user][10] list or [@gethue][11]!

[1]: https://gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2/
[2]: https://gethue.com/hadoop-tutorial-new-impala-and-hive-editors/
[3]: https://youtube.com/watch?v=XakL87LU0pQ
[4]: https://cdn.gethue.com/uploads/2015/11/Assist_complex.png
[5]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_join_alias.png
[6]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_nested_struct.png
[7]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_exploded.png
[8]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_sample_values.png
[9]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_hdfs.png
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
[11]: https://twitter.com/gethue
