---
title: 'New in Cloudera Enterprise 5.9: S3 integration and SQL Editor Improvements'
author: admin
type: post
date: 2014-09-19T21:29:21+00:00
url: /new-in-cloudera-enterprise-5-9-s3-integration-and-sql-editor-improvements/
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


---
**Cloudera Enterprise 5.9 includes the latest release of Hue (3.11), the web UI that makes Apache Hadoop easier to use.

**

As part of Cloudera’s continuing investments in user experience and productivity, <a href="http://blog.cloudera.com/blog/2016/07/cloudera-enterprise-5-8-is-now-available/" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&q=http://blog.cloudera.com/blog/2016/07/cloudera-enterprise-5-8-is-now-available/&source=gmail&ust=1473365323084000&usg=AFQjCNFKYbG5J0FMwNde2EUG83rKGmjmfg" rel="noopener noreferrer">Cloudera Enterprise 5.</a>9 includes a new release of Hue. Hue continues its focus on SQL and also now makes your interaction with the Cloud easier (Amazon S3 specifically in this first version). We’ll provide a summary of the main improvements in the following part of this blog post. (Hue 3.11 is also available for a quick try in one click on <a href="http://demo.gethue.com/" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&q=http://demo.gethue.com/&source=gmail&ust=1473365323084000&usg=AFQjCNE0TBRxA1REwtAUZQTJMjTZoIhlaw" rel="noopener noreferrer">demo.gethue.com</a>.)

# S3 Browser

Hue can be setup to read and write to a configured S3 account, and users can directly query from and save data to S3 without any intermediate moving/copying to HDFS:

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      List, browse buckets, files and directories
    </li>
    <li class="listitem">
      Upload, download any file
    </li>
    <li class="listitem">
      Create external Hive table located on S3
    </li>
    <li class="listitem">
      Export query result directly to S3
    </li>
  </ul>
</div>

[<img src="https://cdn.gethue.com/uploads/2016/08/s3-upload-1024x483.png" sizes="(max-width: 1024px) 100vw, 1024px" srcset="https://cdn.gethue.com/uploads/2016/08/s3-upload-1024x483.png 1024w, /uploads/2016/08/s3-upload-300x142.png 300w, /uploads/2016/08/s3-upload-768x363.png 768w, /uploads/2016/08/s3-upload-1280x604.png 1280w, /uploads/2016/08/s3-upload-800x378.png 800w, /uploads/2016/08/s3-upload.png 1311w"  />][1]

Read more [about it here…][2]

# SQL Autocompleter

Continuing on the focus of making the [SQL query][3] experience better we’ve created a brand new autocompleter. The old one had some limitations and was only aware of parts of the statement being edited. The new autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      Follow the exact SQL grammar of Apache Hive and Impala (incubating)
    </li>
    <li class="listitem">
      Support all the major operations like SELECT, CREATE, DROP, INSERT
    </li>
    <li class="listitem">
      Autocomplete UDFs and show their documentation
    </li>
    <li class="listitem">
      Weight keywords and columns by importance
    </li>
    <li class="listitem">
      Infer the types and propose compatible columns or UDFs
    </li>
  </ul>
</div>

[<img src="https://cdn.gethue.com/uploads/2016/08/sql-autocomp-1024x480.png" sizes="(max-width: 1024px) 100vw, 1024px" srcset="https://cdn.gethue.com/uploads/2016/08/sql-autocomp-1024x480.png 1024w, /uploads/2016/08/sql-autocomp-300x141.png 300w, /uploads/2016/08/sql-autocomp-768x360.png 768w, /uploads/2016/08/sql-autocomp-1280x600.png 1280w, /uploads/2016/08/sql-autocomp-800x375.png 800w, /uploads/2016/08/sql-autocomp.png 1312w" />][4]

Read more [about it here…][5]

# SQL Result Refinements

The SQL Editor now brings a completely re-written result grid that improves the performances allowing big tables to be displayed without the browser to crash, plus some nifty tools for you.

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      Column result search on names, types with quick scrolling
    </li>
    <li class="listitem">
      Optimized to display hundred columns
    </li>
    <li class="listitem">
      Offer to fix certain rows and search through the results
    </li>
    <li class="listitem">
      Info popup when Hive or Impala hangs
    </li>
    <li class="listitem">
      Excel downloads now have a progress status
    </li>
    <li class="listitem">
      Fixed resultset legend and header when scrolling through the results
    </li>
  </ul>
</div>

[<img src="https://cdn.gethue.com/uploads/2016/08/result-refine-1024x542.png" sizes="(max-width: 1024px) 100vw, 1024px" srcset="https://cdn.gethue.com/uploads/2016/08/result-refine-1024x542.png 1024w, /uploads/2016/08/result-refine-300x159.png 300w, /uploads/2016/08/result-refine-768x406.png 768w, /uploads/2016/08/result-refine-1280x677.png 1280w, /uploads/2016/08/result-refine-800x423.png 800w, /uploads/2016/08/result-refine.png 1349w" />][6]

Read more [about it here…][7]

## Security

Recently we have added many security options in HUE. These are turned on by default when possible.

These improvements enables Hue administrators to enforce and manage secure HUE installation. For example, by using the strict-transport-security you can force the browser to communicate solely over HTTPS. Other features include supports for Wildcard certificates, delivering csrftoken and session cookies with secure bit set and security headers like X-XSS-Protection and Content-Security-Policy.

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2016/09/security-response-header.png" sizes="(max-width: 640px) 100vw, 640px" srcset="https://cdn.gethue.com/uploads/2016/09/security-response-header.png 640w, /uploads/2016/09/security-response-header-300x93.png 300w" />][8]

Example of the new headers received with above options

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2016/09/cookie-secured.png" sizes="(max-width: 1065px) 100vw, 1065px" srcset="https://cdn.gethue.com/uploads/2016/09/cookie-secured.png 1065w, /uploads/2016/09/cookie-secured-300x19.png 300w, /uploads/2016/09/cookie-secured-768x48.png 768w, /uploads/2016/09/cookie-secured-1024x63.png 1024w, /uploads/2016/09/cookie-secured-800x50.png 800w" />][9]

Session cookie with secure bit while csrftoken is not

Read more [about it here…][10]

&nbsp;

## Next Up!

Even more SQL improvements are scheduled with a revamped sample popup, tagging capabilities and a smart searching of any tables.

If you have any questions, feel free to comment here, on the <a href="http://groups.google.com/a/cloudera.org/group/hue-user" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&q=http://groups.google.com/a/cloudera.org/group/hue-user&source=gmail&ust=1473365323084000&usg=AFQjCNGMQ_1WCiunG6jNShQqRVWHdfZaWw" rel="noopener noreferrer">hue-user</a> list, or via <a href="https://twitter.com/gethue" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&q=https://twitter.com/gethue&source=gmail&ust=1473365323084000&usg=AFQjCNGntlMpFeJKkpKfaS-7xpGVA8Ur2w" rel="noopener noreferrer">@gethue</a>!

 [1]: https://cdn.gethue.com/uploads/2016/08/s3-upload.png
 [2]: https://gethue.com/introducing-s3-support-in-hue/
 [3]: https://gethue.com/sql-editor-for-solr-sql/
 [4]: https://cdn.gethue.com/uploads/2016/08/sql-autocomp.png
 [5]: https://gethue.com/brand-new-autocompleter-for-hive-and-impala/
 [6]: https://cdn.gethue.com/uploads/2016/08/result-refine.png
 [7]: https://gethue.com/new-features-in-the-sql-results-grid-in-hive-and-impala/
 [8]: https://cdn.gethue.com/uploads/2016/09/security-response-header.png
 [9]: https://cdn.gethue.com/uploads/2016/09/cookie-secured.png
 [10]: https://gethue.com/hue-security-improvements/
