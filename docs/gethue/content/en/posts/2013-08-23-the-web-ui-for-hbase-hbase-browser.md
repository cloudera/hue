---
title: 'The Web UI for HBase: HBase Browser'
author: admin
type: post
date: 2013-08-23T03:28:00+00:00
url: /the-web-ui-for-hbase-hbase-browser/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/59071544309/the-web-ui-for-hbase-hbase-browser
tumblr_gethue_id:
  - 59071544309
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
slide_template:
  - default
categories:
---

<p id="docs-internal-guid-22828246-a92a-294b-6fce-77a2305b7a80">
  In this post, we’ll take a look at the new HBase Browser App added in Hue 2.5.
</p>

&nbsp;

If you want to learn how to create various tables in HBase, go look at [episode 1][1]!

{{< youtube jmcwYCxSwq0 >}}

Prerequisites before starting Hue:

1. Have Hue built or installed

2. Have HBase and Thrift Service 1 initiated (Thrift can be configured through Cloudera Manager or <a href="http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_20_5.html#topic_20_5_4_unique_1" target="_blank" rel="noopener noreferrer">manually</a>). Look at the HBase service configuration and check to see if the "Enable HBase Thrift Server Framed Transport" property is enabled. If it is, try unchecking it or set 'thrift_transport=framed' in the [hbase] section of the hue.ini.

3. Configure your list of HBase Clusters in <a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L467" target="_blank" rel="noopener noreferrer">hue.ini</a> to point to your Thrift IP/Port

<pre><code class="bash">[hbase]

\# Comma-separated list of HBase Thrift servers for clusters in the format of '(name|host:port)'.

hbase_clusters=(Cluster|my-host1:9090),(Cluster2|localhost:9090)

\# Hard limit of rows or columns per row fetched before truncating.

\## truncate_limit = 500

</code></pre>

In this video, we’re walking through two main features of this app.  Let’s talk about HBase Browser!

&nbsp;

&nbsp;

## SmartView

The smartview is the view that you land on when you first enter a table. On the left hand side are the row keys and hovering over a row reveals a list of controls on the right. Click a row to select it, and once selected you can perform batch operations, sort columns, or do any amount of standard database operations. To explore a row, simple scroll to the right. By scrolling, the row should continue to lazily-load cells until the end.

&nbsp;

### Adding Data

To initially populate the table, you can insert a new row or bulk upload CSV/TSV/etc. type data into your table.

<img src="https://lh4.googleusercontent.com/rSmhp0hTq4xtod8SsoIn1A8tp7omHB46j0xtpnmtOQAHzn1PHw1C0rN7Yq8CBq0WOeSh_GVfFWB1P0mKsGGWIpAnGr-mxxJRIR3uW4exevkS5_mKBG0xIbJW" alt="image" width="441px;" height="191px;" />

On the right hand side of a row is a ‘+’ sign that lets you insert columns into your row<img src="https://lh3.googleusercontent.com/2ag5vH82l_6FyCmlBHnQUYCQ8qxsKVQTRoBU_l8oSErvO_4FWKyTyAP5MaZejkLNOy2SQVSNjo47Kq_c2pQB1t67nFB24npZVmONUf3MVivNly7HJutVS7rM" alt="image" width="800px;" height="68px;" /><img src="https://lh4.googleusercontent.com/3aMhyC8qDYdNf98Ge8qbD2EPXzCiL62lCWxHpzhfiYfZPj1F-nAgu3IhbuDYQpTVz1OCqaMDC1WDZ617YfiTsZDafbhHjXufv_f9yyXJbk95fMLNlywLZkHS" alt="image" width="616px;" height="309px;" />

&nbsp;

### Mutating Data

To edit a cell, simply click to edit inline:

<img src="https://lh4.googleusercontent.com/ADTmywVLvEGPordZoEdsOIFkzCWlgc6lG6hrQdtAzT74nHgXqmyto4tPEqqrNmwk0pu709EnP_VIPAgvFPhlPT7NYSDj4LCbApRmw1z-mPyad2jMehWXiZAb" alt="image" width="290px;" height="177px;" />

If you need more control or data about your cell, click “Full Editor” to edit.

<img src="https://lh4.googleusercontent.com/irYJEB6muPCT5Oj3x-LJvMZIhSskXJhIJUsnYL00VpaoYKNTI8NnL09WsmzkxuryFWQpETnUb6EfRkT3ZrrTu7-yAXRDmDCG940Ssh-wbJhaGYt3Sj4txn4T" alt="image" width="620px;" height="639px;" />

In the full editor, you can view cell history or upload binary data to the cell.  Binary data of certain MIME Types are detected, meaning you can view and edit images, PDFs, JSON, XML, and other types directly in your browser!

<img src="https://lh5.googleusercontent.com/N5MqnAhIPQ5D7KSU-ulHTLS0mGFZqC22ciwKGeWhntzpYx4bvqCSvcTc3xCYfCCP6HuxNTr7FlEVMowbSIJ_1nOt36wOXzNpvC-Bhy3gRXve4rIS-Ei6t_By" alt="image" width="635px;" height="371px;" />

&nbsp;

Hovering over a cell also reveals some more controls (such as the delete button or the timestamp).  Click the title to select a few and do batch operations:

<img src="https://lh3.googleusercontent.com/ECcsG6M0zGESG4vuHO8KvgsxrGPbZ5cEhbFxjq2uPhgKzUS-8eTaPq3W2P-rSm13fLxEnEMJY1yFJ8pb2IBmy2KwhGgdFjqQUOTQhQV0sWsxnPFPxpjvoe3T" alt="image" width="497px;" height="153px;" />

If you need some sample data to get started and explore, check out this howto create <a href="http://gethue.tumblr.com/post/58181985680/hadoop-tutorial-how-to-create-example-tables-in-hbase" target="_blank" rel="noopener noreferrer">HBase table tutorial</a>.

&nbsp;

### Smart Searchbar

The “Smart Searchbar” is a sophisticated tool that helps you zero-in on your data. The smart search supports a number of operations.  The most basic ones include finding and scanning row keys.  Here I am selecting two row keys with:

&nbsp;

<pre class="code">domain.100, domain.200</pre>

<img src="https://lh4.googleusercontent.com/2swltMjM0iwMfsN5oL4CAGJvg_2ZEow_swIfUbUqfugC6WfwY7zSlCBeejTTH9u7ixy5w01KKJv4YEoh3ipGTQQrm0PZGgRxXyuqlD4XKS39w3NMVxSHGrx5" alt="image" width="705px;" height="339px;" />

Submitting this query gives me the two rows I was looking for. If I want to fetch rows after one of these, I have to do a scan. This is as easy as writing a ‘+’ followed by the number of rows you want to fetch. Typing in:

&nbsp;

<pre class="code">domain.100, domain.200 +5</pre>

Fetches domain.100 and domain.200 followed by the next 5 rows.  If you’re ever confused about your results, you can look down below and the query bar and also click in to edit your query.

The Smart Search also supports column filtering.  On any row, I can specify the specific columns or families I want to retrieve.  With:

&nbsp;

<pre class="code">domain.100[column_family:]</pre>

I can select a bare family, or mix columns from different families like so:

&nbsp;

<pre class="code">domain.100[family1:, family2:, family3:column_a]</pre>

Doing this will restrict my results from one row key to the columns I specified. If you want to restrict column families only, the same effect can be achieved with the filters on the right.  Just click to toggle a filter.

Finally, let’s try some more complex column filters.  I can query for bare columns:

&nbsp;

<pre class="code">domain.100[column_a]</pre>

This will multiply my query over all column families. I can also do prefixes and scans:

&nbsp;

<pre class="code">    domain.100[family: prefix* +3]</pre>

This will fetch me all columns that start with prefix\* limited to 3 results.  Finally, I can filter on range:

&nbsp;

<pre class="code">domain.100[family: column1 to column100]</pre>

This will fetch me all columns in ‘family:’ that are lexicographically >= column1 but <= column100.  The first column (‘column1’) must be a valid column, but the second can just be any string for comparison.

The Smart Search also supports prefix filtering on rows.  To select a prefixed row, simply type the row key followed by a star \*.  The prefix should be highlighted like any other searchbar keyword.  A prefix scan is performed exactly like a regular scan, but with a prefixed row.

&nbsp;

<pre class="code">domain.10* +10</pre>

Finally, as a new feature, you can also take full advantage of the [HBase filtering][2] language, by typing your filter string between curly braces.  HBase Browser autocompletes your filters for you so you don’t have to look them up every time.  You can apply filters to rows or scans.

&nbsp;

<pre class="code">domain.1000 {ColumnPrefixFilter('100-') AND ColumnCountGetFilter(3)}</pre>

This post only covers a few basic features of the Smart Search. You can take advantage of the full querying language by referring to the help menu when using the app.  These include column prefix, bare columns, column range, etc. Remember that if you ever need help with the searchbar, you can use the help menu that pops up while typing, which will suggest next steps to complete your query.

## Et voila!

Feel free to try the app at [gethue.com][3].  Let us know what you think on the [Hue user group][4]!

Look forward to more features including Thrift 2 support, kerberos security and bulk data upload.

[1]: http://gethue.tumblr.com/post/58181985680/hadoop-tutorial-how-to-create-example-tables-in-hbase
[2]: blank
[3]: http://gethue.com
[4]: https://groups.google.com/a/cloudera.org/forum/#!forum/hue-user
